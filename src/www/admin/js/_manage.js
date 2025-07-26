

export function setCurrentBg( id ) {
    if ( confirm( 'Utiliser comme image de fond?' ) ) {
        const cmd = 'setBg';
        const live = id === 'default' ? 'false' : 'true';

        const url = `/admin/cmd.php?cmd=${ encodeURIComponent( cmd ) }&status=${ encodeURIComponent( live ) }&id=${ encodeURIComponent( id ) }`;
        fetch( url )
            .then( response => response.text() )
            .then( () => {
                window.location.reload();
            } );
    }
}

export function deleteBg( id ) {
    if ( confirm( 'Supprimer cette image?' ) ) {
        const cmd = 'delBg';
        const url = `/admin/cmd.php?cmd=${ encodeURIComponent( cmd ) }&id=${ encodeURIComponent( id ) }`;
        console.log( url );
        fetch( url )
            .then( response => response.text() )
            .then( () => {
                window.location.reload();
            } );
    }
}


export function UiVignettes() {
    vignettes = document.querySelectorAll( '.vignette' );
    vignettes.forEach( vignette => {
        vignette.addEventListener( 'click', function () {
            vignettes.forEach( v => v.classList.remove( 'selected' ) );
            vignette.classList.toggle( 'selected' );
        } );
    } );
}





// Remove the extension
//const fileNameWithoutExt = fileName.split('.').slice(0, -1).join('.');


