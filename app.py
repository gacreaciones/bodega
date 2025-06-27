from flask import Flask, render_template, redirect, url_for, flash, request, session, abort
from extensions import db, bcrypt, login_manager  # <-- Importa db desde extensions
from flask_login import login_user, logout_user, login_required, current_user
from forms import ConsultaDeudaForm, PagoForm, LoginForm, ProductoForm, DeudaForm, ProductoDeudaForm, ClienteForm
from models import Usuario, Cliente, Producto, Deuda, ProductoDeuda, Pago, PagoParcial
from config import Config
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config.from_object(Config)

# Inicializa la base de datos desde extensions
db.init_app(app) 
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ConsultaDeudaForm()
    if form.validate_on_submit():
        apodo = form.apodo.data
        cliente = db.session.execute(
            select(Cliente).filter_by(apodo=apodo)
        ).scalar_one_or_none()
        
        if cliente:
            deudas = db.session.execute(
                select(Deuda).filter_by(cliente_id=cliente.id, estado='pendiente')
            ).scalars().all()
            return render_template('consulta_deuda.html', cliente=cliente, deudas=deudas)
        else:
            flash('No se encontraron deudas para este apodo', 'info')
    return render_template('index.html', form=form)

@app.route('/test_db')
def test_db():
    try:
        db.engine.connect()
        return "Conexión exitosa a Supabase!", 200
    except Exception as e:
        return f"Error de conexión: {str(e)}", 500

@app.route('/pagar/<int:deuda_id>', methods=['GET', 'POST'])
def pagar_deuda(deuda_id):
    deuda = db.session.get(Deuda, deuda_id) or abort(404)
    form = PagoForm()
    
    if form.validate_on_submit():
        pago = Pago(
            deuda_id=deuda.id,
            referencia=form.referencia.data,
            banco_origen=form.banco_origen.data,
            monto_bs=form.monto_bs.data,
            monto_usd=form.monto_usd.data
        )
        deuda.estado = 'pagada'
        db.session.add(pago)
        db.session.commit()
        flash('Pago registrado exitosamente', 'success')
        return redirect(url_for('index'))
    
    return render_template('pagar.html', deuda=deuda, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = db.session.execute(
            select(Usuario).filter_by(username=form.username.data)
        ).scalar_one_or_none()
        
        if usuario and bcrypt.check_password_hash(usuario.password, form.password.data):
            login_user(usuario)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/registrar_cliente', methods=['GET', 'POST'])
@login_required
def registrar_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        cliente = Cliente(
            nombre=form.nombre.data,
            apodo=form.apodo.data
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente registrado exitosamente', 'success')
        return redirect(url_for('listar_clientes'))
    return render_template('registrar_cliente.html', form=form)

@app.route('/clientes')
@login_required
def listar_clientes():
    clientes = db.session.execute(select(Cliente)).scalars().all()
    return render_template('clientes.html', clientes=clientes)

@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    cliente = db.session.get(Cliente, id) or abort(404)
    form = ClienteForm(obj=cliente)
    
    if form.validate_on_submit():
        cliente.nombre = form.nombre.data
        cliente.apodo = form.apodo.data
        db.session.commit()
        flash('Cliente actualizado exitosamente', 'success')
        return redirect(url_for('listar_clientes'))
    
    return render_template('editar_cliente.html', form=form, cliente=cliente)

@app.route('/eliminar_cliente/<int:id>', methods=['POST'])
@login_required
def eliminar_cliente(id):
    cliente = db.session.get(Cliente, id) or abort(404)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado correctamente', 'success')
    return redirect(url_for('listar_clientes'))

@app.route('/registrar_producto', methods=['GET', 'POST'])
@login_required
def registrar_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        producto = Producto(
            nombre=form.nombre.data,
            cantidad=form.cantidad.data,
            precio=form.precio.data
        )
        db.session.add(producto)
        db.session.commit()
        flash('Producto registrado exitosamente', 'success')
        return redirect(url_for('listar_productos'))
    return render_template('registrar_producto.html', form=form)

@app.route('/productos')
@login_required
def listar_productos():
    productos = db.session.execute(select(Producto)).scalars().all()
    return render_template('productos.html', productos=productos)

@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = db.session.get(Producto, id) or abort(404)
    form = ProductoForm(obj=producto)
    
    if form.validate_on_submit():
        producto.nombre = form.nombre.data
        producto.cantidad = form.cantidad.data
        producto.precio = form.precio.data
        db.session.commit()
        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('listar_productos'))
    
    return render_template('editar_producto.html', form=form, producto=producto)

@app.route('/eliminar_producto/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    producto = db.session.get(Producto, id) or abort(404)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado correctamente', 'success')
    return redirect(url_for('listar_productos'))

@app.route('/registrar_deuda', methods=['GET', 'POST'])
@login_required
def registrar_deuda():
    # Inicializar formularios
    deuda_form = DeudaForm()
    producto_form = ProductoDeudaForm()
    
    # Cargar opciones para los select fields
    clientes = Cliente.query.all()
    productos = Producto.query.all()
    
    deuda_form.cliente_id.choices = [(c.id, f"{c.nombre} ({c.apodo})") for c in clientes]
    producto_form.producto_id.choices = [(p.id, p.nombre) for p in productos]

    # Inicializar la lista de productos en sesión si no existe
    if 'productos_deuda' not in session:
        session['productos_deuda'] = []

    # Manejar agregar producto
    if producto_form.validate_on_submit() and producto_form.agregar.data:
        # Validar cantidad disponible
        producto = Producto.query.get(producto_form.producto_id.data)
        if producto and producto.cantidad >= producto_form.cantidad.data:
            session['productos_deuda'].append({
                'producto_id': producto_form.producto_id.data,
                'cantidad': producto_form.cantidad.data
            })
            session.modified = True
            flash('Producto agregado a la deuda', 'success')
        else:
            flash('Cantidad no disponible o producto inválido', 'danger')
        return redirect(url_for('registrar_deuda'))
    
    # Manejar guardar deuda
    if deuda_form.validate_on_submit() and deuda_form.guardar.data:
        if not session['productos_deuda']:
            flash('Debe agregar al menos un producto', 'danger')
            return redirect(url_for('registrar_deuda'))
        
        # Calcular el total de la deuda
        total_deuda = 0
        for item in session['productos_deuda']:
            producto = Producto.query.get(item['producto_id'])
            if producto:
                total_deuda += producto.precio * item['cantidad']
        
        # Obtener cliente
        cliente = Cliente.query.get(deuda_form.cliente_id.data)
        if not cliente:
            flash('Cliente no encontrado', 'danger')
            return redirect(url_for('registrar_deuda'))
        
        # Crear deuda con el total calculado
        deuda = Deuda(
            cliente_id=cliente.id,
            cliente_apodo=cliente.apodo,
        )
        db.session.add(deuda)
        db.session.flush()  # Obtener ID sin commit completo
        
        # Agregar productos y descontar del inventario
        for item in session['productos_deuda']:
            producto = Producto.query.get(item['producto_id'])
            
            # Verificar stock suficiente
            if producto.cantidad < item['cantidad']:
                flash(f'No hay suficiente stock de {producto.nombre}', 'danger')
                db.session.rollback()
                return redirect(url_for('registrar_deuda'))
            
            # Descontar del inventario
            producto.cantidad -= item['cantidad']
            
            # Agregar a la deuda
            p_deuda = ProductoDeuda(
                deuda_id=deuda.id,
                producto_id=producto.id,
                cantidad=item['cantidad']
            )
            db.session.add(p_deuda)
        
        # Limpiar sesión y confirmar cambios
        session.pop('productos_deuda', None)
        db.session.commit()
        
        flash('Deuda registrada exitosamente', 'success')
        return redirect(url_for('registrar_deuda'))  # Recargar para nueva deuda
    
    # Obtener detalles de productos para mostrar
    productos_deuda = []
    for item in session['productos_deuda']:
        producto = Producto.query.get(item['producto_id'])
        if producto:
            productos_deuda.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'cantidad': item['cantidad'],
                'precio': producto.precio,
                'subtotal': producto.precio * item['cantidad']
            })
    
    total = sum(item['subtotal'] for item in productos_deuda) if productos_deuda else 0
    
    return render_template(
        'registrar_deuda.html',
        deuda_form=deuda_form,
        producto_form=producto_form,
        productos_deuda=productos_deuda,
        total=total
    )

@app.route('/eliminar_producto_temp/<int:index>', methods=['POST'])
@login_required
def eliminar_producto_temp(index):
    if 'productos_deuda' in session and 0 <= index < len(session['productos_deuda']):
        session['productos_deuda'].pop(index)
        session.modified = True
    return redirect(url_for('registrar_deuda'))

@app.route('/consulta_deuda_cliente', methods=['GET', 'POST'])
def consulta_deuda_cliente():
    form = ConsultaDeudaForm()
    if form.validate_on_submit():
        apodo = form.apodo.data
        cliente = Cliente.query.filter_by(apodo=apodo).first()
        
        if cliente:
            # Solo mostrar deudas pendientes
            deudas = Deuda.query.filter_by(
                cliente_id=cliente.id, 
                estado='pendiente'
            ).all()
            return render_template('consulta_deuda_cliente.html', cliente=cliente, deudas=deudas)
        else:
            flash('No se encontraron deudas para este apodo', 'info')
    return render_template('index.html', form=form)

# Vista para el dueño (administrativa)
@app.route('/consultar_deudas', methods=['GET'])
@login_required
def consultar_deudas():
    # Obtener parámetros de filtrado
    estado = request.args.get('estado', 'pendiente')
    apodo = request.args.get('apodo')
    
    # Construir consulta base
    query = Deuda.query
    
    # Aplicar filtros
    if estado and estado != 'todos':
        query = query.filter_by(estado=estado)
    
    if apodo:
        query = query.filter(Deuda.cliente_apodo.ilike(f'%{apodo}%'))
    
    # Cargar relaciones necesarias
    query = query.options(
        db.joinedload(Deuda.productos).joinedload(ProductoDeuda.producto),
        db.joinedload(Deuda.pagos_parciales),
        db.joinedload(Deuda.cliente)  # Cargar la relación con cliente
    )
    
    # Obtener resultados ordenados
    deudas = query.order_by(Deuda.fecha.desc()).all()
    
    return render_template('consultar_deudas.html', deudas=deudas)

@app.route('/editar_deuda/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_deuda(id):
    deuda = db.session.get(Deuda, id) or abort(404)
    
    # Obtener todos los clientes
    clientes = db.session.execute(select(Cliente)).scalars().all()
    
    # Crear formulario
    deuda_form = DeudaForm()
    deuda_form.cliente_id.choices = [(c.id, f"{c.nombre} ({c.apodo})") for c in clientes]
    deuda_form.cliente_id.data = deuda.cliente_id
    
    # Formulario para agregar productos
    producto_form = ProductoDeudaForm()
    producto_form.producto_id.choices = [(p.id, p.nombre) for p in Producto.query.all()]
    
    # Inicializar la sesión si no existe
    if 'productos_deuda' not in session:
        session['productos_deuda'] = []
        # Cargar productos existentes
        for producto_deuda in deuda.productos:
            session['productos_deuda'].append({
                'producto_id': producto_deuda.producto_id,
                'cantidad': producto_deuda.cantidad
            })
    
    if producto_form.agregar.data and producto_form.validate():
        session['productos_deuda'].append({
            'producto_id': producto_form.producto_id.data,
            'cantidad': producto_form.cantidad.data
        })
        session.modified = True
        return redirect(url_for('editar_deuda', id=id))
    
    if deuda_form.guardar.data and deuda_form.validate():
     new_cliente_id = deuda_form.cliente_id.data
     new_cliente = db.session.get(Cliente, new_cliente_id)
    
    if not new_cliente:
        flash('Cliente no encontrado', 'danger')
        return redirect(url_for('editar_deuda', id=id))
    
    # Actualizar cliente asociado
    deuda.cliente_id = new_cliente_id
    deuda.cliente_apodo = new_cliente.apodo
    
    # Eliminar productos antiguos
    ProductoDeuda.query.filter_by(deuda_id=deuda.id).delete()
    
    # Agregar nuevos productos
    for item in session['productos_deuda']:
        producto_deuda = ProductoDeuda(
            deuda_id=deuda.id,
            producto_id=item['producto_id'],
            cantidad=item['cantidad']
        )
        db.session.add(producto_deuda)
    
     # Limpiar sesión
    session.pop('productos_deuda', None)
    db.session.commit()
    

    flash('Deuda actualizada exitosamente', 'success')
    return redirect(url_for('consultar_deudas'))

@app.route('/gestion_deudas/<int:cliente_id>', methods=['GET'])
@login_required
def gestion_deudas(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    
    # Cargar relaciones necesarias con joinedload
    deudas = Deuda.query.filter_by(cliente_id=cliente.id).options(
        db.joinedload(Deuda.productos).joinedload(ProductoDeuda.producto),
        db.joinedload(Deuda.pagos_parciales)
    ).all()
    
    return render_template('gestion_deudas.html', cliente=cliente, deudas=deudas)

@app.route('/marcar_pagada/<int:deuda_id>', methods=['POST'])
@login_required
def marcar_pagada(deuda_id):
    deuda = Deuda.query.get_or_404(deuda_id)
    deuda.estado = 'pagada'
    db.session.commit()
    flash('Deuda marcada como pagada', 'success')
    return redirect(url_for('gestion_deudas', cliente_id=deuda.cliente_id))

@app.route('/eliminar_producto_temp/<int:index>/<int:deuda_id>', methods=['POST'])
@login_required
def eliminar_producto_deuda_temp(index, deuda_id):
    if 'productos_deuda' in session and index < len(session['productos_deuda']):
        session['productos_deuda'].pop(index)
        session.modified = True
    return redirect(url_for('editar_deuda', id=deuda_id))


@app.route('/registrar_pago_parcial/<int:deuda_id>', methods=['POST'])
@login_required
def registrar_pago_parcial(deuda_id):
    deuda = Deuda.query.get_or_404(deuda_id)
    monto = float(request.form.get('monto'))
    descripcion = request.form.get('descripcion', 'Pago parcial')
    
    if monto <= 0:
        flash('El monto debe ser mayor a cero', 'danger')
        return redirect(url_for('gestion_deudas', cliente_id=deuda.cliente_id))
    
    if monto > deuda.saldo_pendiente:
        flash('El monto excede el saldo pendiente', 'danger')
        return redirect(url_for('gestion_deudas', cliente_id=deuda.cliente_id))
    
    nuevo_pago = PagoParcial(
        deuda_id=deuda.id,
        monto_usd=monto,
        descripcion=descripcion
    )
    
    db.session.add(nuevo_pago)
    
    # Si el pago cubre todo el saldo, marcar como pagada
    if deuda.saldo_pendiente - monto <= 0:
        deuda.estado = 'pagada'
    
    db.session.commit()
    flash('Pago parcial registrado exitosamente', 'success')
    return redirect(url_for('gestion_deudas', cliente_id=deuda.cliente_id))

@app.route('/eliminar_deuda/<int:id>', methods=['POST'])
@login_required
def eliminar_deuda(id):
    deuda = db.session.get(Deuda, id) or abort(404)
    
    # Eliminar productos asociados
    ProductoDeuda.query.filter_by(deuda_id=id).delete()
    
    # Eliminar la deuda
    db.session.delete(deuda)
    db.session.commit()
    
    flash('Deuda eliminada correctamente', 'success')
    return redirect(url_for('consultar_deudas'))

if __name__ == '__main__':
    app.run(debug=True)
