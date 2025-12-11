/**
 * Validaciones del Sistema Clínica Jurídica
 * ISO/IEC 25010 - Usabilidad
 */

// =============================================================================
// VALIDACIÓN DE RUT CHILENO
// =============================================================================

function limpiarRut(rut) {
    return rut.replace(/[.\-\s]/g, '').toUpperCase();
}

function calcularDigitoVerificador(rutNumero) {
    let suma = 0;
    let multiplicador = 2;
    
    for (let i = rutNumero.length - 1; i >= 0; i--) {
        suma += parseInt(rutNumero[i]) * multiplicador;
        multiplicador = multiplicador < 7 ? multiplicador + 1 : 2;
    }
    
    const resto = suma % 11;
    const dv = 11 - resto;
    
    if (dv === 11) return '0';
    if (dv === 10) return 'K';
    return dv.toString();
}

function validarRut(rut) {
    if (!rut) return { valido: true, mensaje: '' };
    
    const rutLimpio = limpiarRut(rut);
    
    if (rutLimpio.length < 2) {
        return { valido: false, mensaje: 'El RUT es muy corto' };
    }
    
    const rutNumero = rutLimpio.slice(0, -1);
    const dvIngresado = rutLimpio.slice(-1);
    
    if (!/^\d+$/.test(rutNumero)) {
        return { valido: false, mensaje: 'El RUT debe contener solo números' };
    }
    
    const rutInt = parseInt(rutNumero);
    if (rutInt < 1000000 || rutInt > 99999999) {
        return { valido: false, mensaje: 'El RUT está fuera de rango' };
    }
    
    const dvCalculado = calcularDigitoVerificador(rutNumero);
    
    if (dvIngresado !== dvCalculado) {
        return { valido: false, mensaje: 'El dígito verificador es inválido' };
    }
    
    return { valido: true, mensaje: 'RUT válido' };
}

function formatearRut(rut) {
    const rutLimpio = limpiarRut(rut);
    
    if (rutLimpio.length < 2) return rut;
    
    const rutNumero = rutLimpio.slice(0, -1);
    const dv = rutLimpio.slice(-1);
    
    let rutFormateado = '';
    for (let i = rutNumero.length - 1, j = 0; i >= 0; i--, j++) {
        if (j > 0 && j % 3 === 0) {
            rutFormateado = '.' + rutFormateado;
        }
        rutFormateado = rutNumero[i] + rutFormateado;
    }
    
    return `${rutFormateado}-${dv}`;
}

// =============================================================================
// VALIDACIÓN DE TELÉFONO CHILENO
// =============================================================================

function validarTelefono(telefono) {
    if (!telefono) return { valido: true, mensaje: '' };
    
    const telefonoLimpio = telefono.replace(/[\s\-\(\)]/g, '');
    
    const patrones = [
        /^\+569\d{8}$/,
        /^569\d{8}$/,
        /^9\d{8}$/,
        /^\+562\d{8}$/,
        /^2\d{8}$/
    ];
    
    for (const patron of patrones) {
        if (patron.test(telefonoLimpio)) {
            return { valido: true, mensaje: 'Teléfono válido' };
        }
    }
    
    return { valido: false, mensaje: 'Formato inválido. Ej: +56 9 1234 5678' };
}

function formatearTelefono(telefono) {
    if (!telefono) return '';
    
    let telefonoLimpio = telefono.replace(/[\s\-\(\)\+]/g, '');
    
    if (telefonoLimpio.startsWith('56')) {
        telefonoLimpio = telefonoLimpio.slice(2);
    }
    
    if (telefonoLimpio.length === 9 && telefonoLimpio.startsWith('9')) {
        return `+56 ${telefonoLimpio[0]} ${telefonoLimpio.slice(1, 5)} ${telefonoLimpio.slice(5)}`;
    }
    
    return telefono;
}

// =============================================================================
// VALIDACIÓN DE EMAIL
// =============================================================================

function validarEmail(email) {
    if (!email) return { valido: true, mensaje: '' };
    
    const patron = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    
    if (patron.test(email)) {
        return { valido: true, mensaje: 'Email válido' };
    }
    
    return { valido: false, mensaje: 'Ingresa un email válido' };
}

// =============================================================================
// VALIDACIÓN DE CONTRASEÑA
// =============================================================================

function validarPassword(password) {
    const requisitos = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /\d/.test(password),
    };
    
    // Actualizar visualización de requisitos
    const reqElements = {
        'req-length': requisitos.length,
        'req-uppercase': requisitos.uppercase,
        'req-lowercase': requisitos.lowercase,
        'req-number': requisitos.number,
    };
    
    for (const [id, cumple] of Object.entries(reqElements)) {
        const element = document.getElementById(id);
        if (element) {
            const icon = element.querySelector('i');
            if (cumple) {
                element.classList.add('requirement-met');
                element.classList.remove('requirement-unmet');
                if (icon) icon.className = 'fas fa-check-circle';
            } else {
                element.classList.add('requirement-unmet');
                element.classList.remove('requirement-met');
                if (icon) icon.className = 'fas fa-circle';
            }
        }
    }
    
    return requisitos;
}

// =============================================================================
// APLICAR VALIDACIONES A FORMULARIOS
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // Validación de RUT en tiempo real
    document.querySelectorAll('input[name="run"], input[name="rut"]').forEach(input => {
        const feedbackId = input.id + '-feedback';
        let feedback = document.getElementById(feedbackId);
        
        if (!feedback) {
            feedback = document.createElement('span');
            feedback.id = feedbackId;
            feedback.className = 'field-feedback';
            input.parentNode.appendChild(feedback);
        }
        
        input.addEventListener('blur', function() {
            const resultado = validarRut(this.value);
            
            if (this.value) {
                this.value = formatearRut(this.value);
            }
            
            feedback.textContent = resultado.mensaje;
            feedback.className = 'field-feedback ' + (resultado.valido ? 'feedback-success' : 'feedback-error');
            input.classList.toggle('input-error', !resultado.valido);
            input.classList.toggle('input-success', resultado.valido && this.value);
        });
    });
    
    // Validación de teléfono en tiempo real
    document.querySelectorAll('input[name="telefono"]').forEach(input => {
        const feedbackId = input.id + '-feedback';
        let feedback = document.getElementById(feedbackId);
        
        if (!feedback) {
            feedback = document.createElement('span');
            feedback.id = feedbackId;
            feedback.className = 'field-feedback';
            input.parentNode.appendChild(feedback);
        }
        
        input.addEventListener('blur', function() {
            const resultado = validarTelefono(this.value);
            
            if (this.value && resultado.valido) {
                this.value = formatearTelefono(this.value);
            }
            
            feedback.textContent = resultado.mensaje;
            feedback.className = 'field-feedback ' + (resultado.valido ? 'feedback-success' : 'feedback-error');
            input.classList.toggle('input-error', !resultado.valido);
            input.classList.toggle('input-success', resultado.valido && this.value);
        });
    });
    
    // Validación de email en tiempo real
    document.querySelectorAll('input[type="email"]').forEach(input => {
        const feedbackId = input.id + '-feedback';
        let feedback = document.getElementById(feedbackId);
        
        if (!feedback) {
            feedback = document.createElement('span');
            feedback.id = feedbackId;
            feedback.className = 'field-feedback';
            input.parentNode.appendChild(feedback);
        }
        
        input.addEventListener('blur', function() {
            const resultado = validarEmail(this.value);
            
            feedback.textContent = resultado.mensaje;
            feedback.className = 'field-feedback ' + (resultado.valido ? 'feedback-success' : 'feedback-error');
            input.classList.toggle('input-error', !resultado.valido);
            input.classList.toggle('input-success', resultado.valido && this.value);
        });
    });
    
    // Prevenir envío de formulario con errores
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const errores = this.querySelectorAll('.input-error');
            
            if (errores.length > 0) {
                e.preventDefault();
                errores[0].focus();
                alert('Por favor, corrige los errores en el formulario antes de continuar.');
            }
        });
    });
});