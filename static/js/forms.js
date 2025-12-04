// Basic client-side validation and notifications
document.addEventListener('DOMContentLoaded', function(){
    // Auto-dismiss alerts after 6s
    const alerts = document.querySelectorAll('#messages .alert');
    alerts.forEach(a => {
        const close = a.querySelector('.alert-close');
        if(close) close.addEventListener('click', ()=> a.remove());
        setTimeout(()=>{ try{ a.remove() }catch(e){} }, 6000);
    });

    // Attach to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e){
            // Only validate forms that have at least one input with class 'form-input'
            const inputs = form.querySelectorAll('.form-input');
            if(!inputs.length) return true;
            let valid = true;
            // clear previous inline errors
            form.querySelectorAll('.inline-error').forEach(el => el.remove());

            inputs.forEach(inp => {
                const name = inp.getAttribute('name') || '';
                const val = inp.value.trim();
                // run validation for RUT
                if(name === 'run'){
                    const rutRegex = /^\d{1,3}(?:\.\d{3})*-?[0-9kK]$/;
                    if(val && !rutRegex.test(val)){
                        showInlineError(inp, 'Formato RUT inválido. Ej: 12.345.678-9');
                        valid = false;
                    }
                }
                if(name === 'telefono'){
                    const telRegex = /^[\d\s\+\-\(\)]+$/;
                    if(val && !telRegex.test(val)){
                        showInlineError(inp, 'Teléfono contiene caracteres inválidos.');
                        valid = false;
                    }
                }
                if(inp.type === 'email'){
                    if(val && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)){
                        showInlineError(inp, 'Ingrese un correo válido.');
                        valid = false;
                    }
                }
                // required attribute fallback: if required attr present and empty
                if(inp.hasAttribute('required') && !val){
                    showInlineError(inp, 'Campo requerido.');
                    valid = false;
                }
            });

            if(!valid){
                e.preventDefault();
                scrollToFirstError();
            }
        });
    });

    function showInlineError(input, msg){
        const err = document.createElement('div');
        err.className = 'inline-error';
        err.textContent = msg;
        input.parentNode.appendChild(err);
    }
    function scrollToFirstError(){
        const err = document.querySelector('.inline-error');
        if(err){
            err.scrollIntoView({behavior:'smooth', block:'center'});
            err.classList.add('pulse');
        }
    }
});
