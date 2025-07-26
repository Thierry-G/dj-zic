
import { H1, H1t, BG, BGt, ALERT_BORDER } from './_Colors.js';

export function setAlert( djNameInput, djNameError, changeName, message ) {
   ;
    djNameError.style.width = `${ djNameInput.getBoundingClientRect().width}px`;
    djNameError.style.marginTop = '-4px';
    djNameInput.style.border = '2px solid rgb(255, 103, 35) !important';
    djNameError.innerHTML = `<img src="/img/alert.svg" alt="alert"><span>${ message }</span>`;
    djNameError.classList.remove( 'hide' );
    changeName.disabled = true;
    djNameInput.classList.toggle( 'selected' );
    djNameInput.style.backgroundColor = BG;
    djNameInput.style.border = `3px solid ${ ALERT_BORDER }`;
    djNameInput.focus();
}

export function closeModal() {
    modal.classList.toggle( 'hide' );
    modalMessage.classList.toggle( 'hide' );
    modalMessage.innerHTML = '';

}