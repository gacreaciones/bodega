from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, NumberRange

class ConsultaDeudaForm(FlaskForm):
    apodo = StringField('Apodo', validators=[DataRequired(), Length(min=2, max=50)])
    consultar = SubmitField('Consultar Deuda')

class PagoForm(FlaskForm):
    referencia = StringField('Número de Referencia', validators=[DataRequired()])
    banco_origen = StringField('Banco de Origen', validators=[DataRequired()])
    monto_usd = FloatField('Monto en Dólares', validators=[DataRequired(), NumberRange(min=0.01)])
    pagar = SubmitField('Registrar Pago')

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Producto', validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=1)])
    precio = FloatField('Precio (USD)', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Guardar Producto')

class ClienteForm(FlaskForm):  # Nuevo formulario
    nombre = StringField('Nombre Completo', validators=[DataRequired()])
    apodo = StringField('Apodo', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Guardar Cliente')

class DeudaForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    guardar = SubmitField('Guardar Deuda')

class ProductoDeudaForm(FlaskForm):
    producto_id = SelectField('Producto', coerce=int, validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=1)])
    agregar = SubmitField('Agregar Producto')