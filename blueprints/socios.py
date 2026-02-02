from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, current_app
from flask_login import login_required, current_user
from models import User, Actividad, Inscripcion, Beneficiario, db
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageTemplate, Frame
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

socios_bp = Blueprint('socios', __name__)

@socios_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_socio():
        flash('No tienes permisos para acceder a esta página.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Todas las actividades disponibles
    actividades_disponibles = Actividad.query.filter(
        Actividad.fecha > datetime.utcnow()
    ).order_by(Actividad.fecha).all()
    
    # Obtener todas las inscripciones del socio (suyas y de sus beneficiarios)
    inscripciones = Inscripcion.query.filter_by(user_id=current_user.id).all()
    
    # Obtener actividades únicas de las inscripciones
    actividades_ids = {insc.actividad_id for insc in inscripciones}
    actividades_inscrito = Actividad.query.filter(Actividad.id.in_(actividades_ids)).order_by(Actividad.fecha).all()
    
    # Crear un diccionario de inscripciones por actividad
    inscripciones_por_actividad = {}
    for insc in inscripciones:
        if insc.actividad_id not in inscripciones_por_actividad:
            inscripciones_por_actividad[insc.actividad_id] = []
        inscripciones_por_actividad[insc.actividad_id].append(insc)
    
    # Cargar beneficiarios del socio
    beneficiarios = Beneficiario.query.filter_by(socio_id=current_user.id).order_by(Beneficiario.nombre).all()
    
    return render_template('socios/dashboard.html',
                         actividades_disponibles=actividades_disponibles,
                         actividades_inscrito=actividades_inscrito,
                         inscripciones_por_actividad=inscripciones_por_actividad,
                         beneficiarios=beneficiarios)

@socios_bp.route('/perfil')
@login_required
def perfil():
    if not current_user.is_socio():
        flash('No tienes permisos para acceder a esta página.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('socios/perfil.html', usuario=current_user)

@socios_bp.route('/actividades')
@login_required
def actividades():
    if not current_user.is_socio():
        flash('No tienes permisos para acceder a esta página.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Todas las actividades disponibles
    actividades = Actividad.query.filter(
        Actividad.fecha > datetime.utcnow()
    ).order_by(Actividad.fecha).all()
    
    # Cargar beneficiarios del socio
    beneficiarios = Beneficiario.query.filter_by(socio_id=current_user.id).order_by(Beneficiario.nombre).all()
    
    return render_template('socios/actividades.html', actividades=actividades, beneficiarios=beneficiarios)

@socios_bp.route('/actividades/<int:actividad_id>/inscribir', methods=['POST'])
@login_required
def inscribir_actividad(actividad_id):
    if not current_user.is_socio():
        flash('No tienes permisos para realizar esta acción.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    actividad = Actividad.query.get_or_404(actividad_id)
    beneficiario_id = request.form.get('beneficiario_id', '').strip()
    
    # Determinar si es inscripción del socio o de un beneficiario
    es_beneficiario = beneficiario_id and beneficiario_id != 'socio'
    beneficiario = None
    ano_nacimiento = None
    nombre_inscrito = current_user.nombre
    
    if es_beneficiario:
        try:
            beneficiario_id_int = int(beneficiario_id)
            # Verificar que el beneficiario pertenece al socio
            beneficiario = Beneficiario.query.filter_by(id=beneficiario_id_int, socio_id=current_user.id).first()
            if not beneficiario:
                flash('El beneficiario no pertenece a tu cuenta.', 'error')
                return redirect(url_for('socios.actividades'))
            
            # Verificar si el beneficiario ya está inscrito
            if actividad.beneficiario_inscrito(beneficiario_id_int):
                flash(f'{beneficiario.nombre} ya está inscrito en esta actividad.', 'warning')
                return redirect(url_for('socios.actividades'))
            
            ano_nacimiento = beneficiario.ano_nacimiento
            nombre_inscrito = f"{beneficiario.nombre} {beneficiario.primer_apellido}"
        except ValueError:
            flash('ID de beneficiario inválido.', 'error')
            return redirect(url_for('socios.actividades'))
    else:
        # Verificar si el socio ya está inscrito
        if actividad.usuario_inscrito(current_user.id):
            flash('Ya estás inscrito en esta actividad.', 'warning')
            return redirect(url_for('socios.actividades'))
        
        ano_nacimiento = current_user.ano_nacimiento
    
    # Verificar si hay plazas disponibles
    if not actividad.tiene_plazas_disponibles():
        flash('No hay plazas disponibles para esta actividad.', 'error')
        return redirect(url_for('socios.actividades'))
    
    # Verificar si la actividad no ha pasado
    if actividad.fecha <= datetime.utcnow():
        flash('Esta actividad ya ha terminado.', 'error')
        return redirect(url_for('socios.actividades'))
    
    # Verificar restricción de edad
    if actividad.tiene_restriccion_edad():
        puede_inscribirse, mensaje_error = actividad.puede_inscribirse_por_edad(ano_nacimiento)
        if not puede_inscribirse:
            flash(f'No se puede inscribir en esta actividad: {mensaje_error}', 'error')
            return redirect(url_for('socios.actividades'))
    
    # Crear inscripción
    inscripcion = Inscripcion(
        user_id=current_user.id,
        actividad_id=actividad.id,
        beneficiario_id=beneficiario.id if es_beneficiario else None
    )
    
    try:
        db.session.add(inscripcion)
        db.session.commit()
        
        if es_beneficiario:
            flash(f'{nombre_inscrito} se ha inscrito exitosamente en "{actividad.nombre}".', 'success')
        else:
            flash(f'Te has inscrito exitosamente en "{actividad.nombre}".', 'success')
        
        return redirect(url_for('socios.dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al inscribirse en la actividad: {str(e)}. Por favor, inténtalo de nuevo.', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('socios.actividades'))

@socios_bp.route('/actividades/<int:actividad_id>/cancelar', methods=['POST'])
@login_required
def cancelar_inscripcion(actividad_id):
    if not current_user.is_socio():
        flash('No tienes permisos para realizar esta acción.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    actividad = Actividad.query.get_or_404(actividad_id)
    beneficiario_id = request.form.get('beneficiario_id', '').strip()
    
    # Buscar la inscripción (socio o beneficiario)
    inscripcion = None
    nombre_cancelar = "tu inscripción"
    
    if beneficiario_id and beneficiario_id != 'socio':
        # Es una inscripción de beneficiario
        try:
            beneficiario_id_int = int(beneficiario_id)
            # Verificar que el beneficiario pertenece al socio
            beneficiario = Beneficiario.query.filter_by(id=beneficiario_id_int, socio_id=current_user.id).first()
            if not beneficiario:
                flash('El beneficiario no pertenece a tu cuenta.', 'error')
                return redirect(url_for('socios.dashboard'))
            
            inscripcion = Inscripcion.query.filter_by(
                user_id=current_user.id,
                actividad_id=actividad_id,
                beneficiario_id=beneficiario_id_int
            ).first()
            
            if inscripcion:
                nombre_cancelar = f"{beneficiario.nombre} {beneficiario.primer_apellido}"
        except (ValueError, TypeError):
            flash('ID de beneficiario inválido.', 'error')
            return redirect(url_for('socios.dashboard'))
    else:
        # Es una inscripción del socio (beneficiario_id es None o 'socio')
        inscripcion = Inscripcion.query.filter_by(
            user_id=current_user.id,
            actividad_id=actividad_id,
            beneficiario_id=None
        ).first()
    
    if not inscripcion:
        if beneficiario_id and beneficiario_id != 'socio':
            flash('El beneficiario no está inscrito en esta actividad.', 'error')
        else:
            flash('No estás inscrito en esta actividad.', 'error')
        return redirect(url_for('socios.dashboard'))
    
    # Permitir cancelar en cualquier momento (sin restricción de tiempo)
    try:
        db.session.delete(inscripcion)
        db.session.commit()
        
        if beneficiario_id and beneficiario_id != 'socio':
            flash(f'Has cancelado la inscripción de {nombre_cancelar} en "{actividad.nombre}".', 'success')
        else:
            flash(f'Has cancelado tu inscripción en "{actividad.nombre}".', 'success')
        
        return redirect(url_for('socios.dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cancelar la inscripción: {str(e)}. Por favor, inténtalo de nuevo.', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('socios.dashboard'))

@socios_bp.route('/mis-actividades')
@login_required
def mis_actividades():
    if not current_user.is_socio():
        flash('No tienes permisos para acceder a esta página.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Obtener todas las inscripciones del socio (suyas y de sus beneficiarios)
    inscripciones = Inscripcion.query.filter_by(user_id=current_user.id).all()
    
    # Obtener actividades únicas de las inscripciones
    actividades_ids = {insc.actividad_id for insc in inscripciones}
    actividades_inscrito = Actividad.query.filter(Actividad.id.in_(actividades_ids)).order_by(Actividad.fecha).all()
    
    # Crear un diccionario de inscripciones por actividad
    inscripciones_por_actividad = {}
    for insc in inscripciones:
        if insc.actividad_id not in inscripciones_por_actividad:
            inscripciones_por_actividad[insc.actividad_id] = []
        inscripciones_por_actividad[insc.actividad_id].append(insc)
    
    return render_template('socios/mis_actividades.html', 
                         actividades=actividades_inscrito,
                         inscripciones_por_actividad=inscripciones_por_actividad,
                         ahora=datetime.utcnow())

@socios_bp.route('/descargar-carnet')
@login_required
def descargar_carnet():
    """Genera un PDF con el carnet del socio"""
    if not current_user.is_socio():
        flash('No tienes permisos para acceder a esta página.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    # Cargar beneficiarios del socio
    beneficiarios = Beneficiario.query.filter_by(socio_id=current_user.id).order_by(Beneficiario.nombre).all()
    
    try:
        buffer = BytesIO()
        
        # Función para dibujar el fondo azul - se ejecutará en cada página
        def add_background(canvas, doc):
            # Dibujar el fondo azul que cubre toda la página
            canvas.saveState()
            canvas.setFillColor(colors.HexColor('#E3F2FD'))
            canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
            canvas.restoreState()
        
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=1*cm, bottomMargin=2*cm,
                                onFirstPage=add_background,
                                onLaterPages=add_background)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#333333'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        normal_style = styles['Normal']
        bold_style = ParagraphStyle(
            'BoldStyle',
            parent=normal_style,
            fontSize=11,
            fontName='Helvetica-Bold'
        )
        
        story = []
        
        # Logo del carnet
        logo_path = os.path.join(current_app.root_path, 'static', 'logo_carnet.jpg')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=300, height=200)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 0.5*cm))
        
        # Título con año en curso
        año_actual = datetime.now().year
        story.append(Paragraph(f"CARNET DE SOCIO {año_actual}", title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Datos del socio
        story.append(Paragraph("Datos del Socio", bold_style))
        story.append(Spacer(1, 0.2*cm))
        
        # Crear tabla con los datos del socio
        fecha_validez_str = current_user.fecha_validez.strftime('%d/%m/%Y') if current_user.fecha_validez else 'No especificada'
        datos_socio = [
            [Paragraph("Nombre:", bold_style), Paragraph(current_user.nombre, normal_style)],
            [Paragraph("Número de Socio:", bold_style), Paragraph(current_user.numero_socio or 'No asignado', normal_style)],
            [Paragraph("Fecha de Alta:", bold_style), Paragraph(current_user.fecha_alta.strftime('%d/%m/%Y') if current_user.fecha_alta else 'No especificada', normal_style)],
            [Paragraph("Válido hasta:", bold_style), Paragraph(fecha_validez_str, bold_style)],
        ]
        
        # Agregar dirección si está disponible
        if current_user.calle and current_user.numero and current_user.poblacion:
            direccion = f"{current_user.calle} {current_user.numero}"
            if current_user.piso:
                direccion += f", {current_user.piso}"
            direccion += f", {current_user.poblacion}"
            datos_socio.append([Paragraph("Dirección:", bold_style), Paragraph(direccion, normal_style)])
        
        table_socio = Table(datos_socio, colWidths=[5*cm, 11*cm])
        table_socio.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(table_socio)
        
        # Beneficiarios
        if beneficiarios:
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph("Beneficiarios", bold_style))
            story.append(Spacer(1, 0.2*cm))
            
            datos_beneficiarios = [
                [Paragraph("Nombre", bold_style), Paragraph("Primer Apellido", bold_style), 
                 Paragraph("Segundo Apellido", bold_style), Paragraph("Año Nacimiento", bold_style)]
            ]
            
            for beneficiario in beneficiarios:
                datos_beneficiarios.append([
                    Paragraph(beneficiario.nombre, normal_style),
                    Paragraph(beneficiario.primer_apellido, normal_style),
                    Paragraph(beneficiario.segundo_apellido or '', normal_style),
                    Paragraph(str(beneficiario.ano_nacimiento), normal_style)
                ])
            
            table_beneficiarios = Table(datos_beneficiarios, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
            table_beneficiarios.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ]))
            story.append(table_beneficiarios)
        
        # Construir el PDF - el callback dibujará el fondo en cada página
        doc.build(story)
        buffer.seek(0)
        pdf_bytes = buffer.read()
        
    except Exception as e:
        flash(f'No se pudo generar el carnet: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('socios.dashboard'))
    
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    nombre_archivo = f"carnet_socio_{current_user.numero_socio or current_user.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    response.headers['Content-Disposition'] = f'inline; filename={nombre_archivo}'
    
    return response
