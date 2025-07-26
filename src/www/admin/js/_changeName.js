export const maxChars = 144;

export function verifyField( value ) {

    if ( value.length === 0 || !value.trim() ) {
        return 'Le champ ne doit pas être vide.';
    }
    const dangerousChars = /<script>|<\/script>|[<>]/gi;
    if ( dangerousChars.test( value ) ) {
        return 'Le champ contient des caractères interdits.';
    }
    return;
}

export function addPictClose() {
    const actionUi = document.getElementById( 'actionScreen' );
    const AddPict = document.getElementById( 'AddPict' );
    document.querySelector( '.header' ).classList.toggle( "hide" );
    document.querySelector( '.content' ).classList.toggle( "hide" );
    document.querySelector( '.footer' ).classList.toggle( "hide" );
    actionUi.classList.toggle( 'hide' );
    AddPict.classList.toggle( 'hide' );
}

export function adjustTextareaHeight( textarea ) {
    textarea.style.height = "auto"; // Reset height to avoid incorrect calculations
    textarea.style.height = `${ textarea.scrollHeight }px`; // Adjust based on content
}

export function showHideDjName() {

    const remaining = maxChars - djNameInput.value.length;
    charCount.textContent = `${ remaining }`;

    djPictMenu.classList.toggle( 'hide' );
    djNameMenu.classList.toggle( 'closed' );
    djNameBtn.classList.toggle( 'selected' );
    djNameMenu.classList.remove( 'selected' );
    djNameMenu.querySelector( 'h2' ).classList.toggle( 'hide' );
    djNameMenu.querySelector( '.modify.selected' ).classList.toggle( 'hide' );
    djNameInput.classList.toggle( 'hide' );
    adjustTextareaHeight( djNameInput );
}


export function showHideDjPict() {
    djNameMenu.classList.toggle( 'hide' );
    djPictBtn.classList.toggle( 'selected' );

    djPictMenu.classList.toggle( 'closed' );
    djPictMenu.classList.toggle( 'selected' );
    djPictMenu.querySelector( '#djPictEdit' ).classList.toggle( 'hide' );
}

