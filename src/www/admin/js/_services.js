

function closeModal() {
    modal.classList.toggle('hide');
    modalMessage.classList.add( 'hide' );
    modalMessage.innerHTML = '';
}

async function checkServerStatus(ip, maxAttempts = 30, interval = 2000) {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            const response = await fetch(`http://${ip}/admin/`);
            if (response.ok) {
                modalConfirm.classList.toggle('hide');
                modalMessage.classList.toggle('hide');
                location.reload();
                return;
            }
        } catch (error) {
            console.error(`Attempt ${attempt}: Server not available yet`);
        }
        // Wait before the next attempt
        await new Promise(resolve => setTimeout(resolve, interval));
    }

    // If we reach maxAttempts without success
    modalMessage.innerHTML = '<h1>Échec du redémarrage</h1><p>Le serveur ne répond pas.<br>Veuillez vérifier sa connexion.</p>';
}

export function toggleServiceList( header ) {
    const serviceList = header.nextElementSibling;
    const chevron = header.querySelector( '.chevron' );
    if ( serviceList.style.display === 'none' || serviceList.style.display === '' ) {
        serviceList.style.display = 'flex';
        chevron.classList.remove( 'collapsed' );
    } else {
        serviceList.style.display = 'none';
        chevron.classList.add( 'collapsed' );
    }
}

export function showHideLoader( loading ) {
    //const loading = document.getElementById('serviceLoader');
    const loader = loading.nextElementSibling;
    loader.classList.toggle('hide');
    loader.nextElementSibling.classList.toggle('hide');
}

export function rebootServer( type, isLocal, ip ) {
    modal.classList.toggle('hide');
    const modalConfirm = modal.querySelector( '.modal-confirm');
    const modalMessage = modal.querySelector( '.modal-content' );

    const confirm = document.getElementById( 'confirm' );
    const confirmButton = document.getElementById( 'confirmButton' );
    const cancelButton = document.getElementById( 'cancelButton' );
    confirm.innerHTML = isLocal === true ? `Le redémarrage du ${ type }.` : `Le redémarrage du ${ type } (${ ip }).`
    modalConfirm.classList.toggle('hide');

    cancelButton.addEventListener( 'click', () => {
        modal.classList.toggle('hide');
    } );

    confirmButton.addEventListener( 'click', () => {

        modalConfirm.classList.toggle('hide');
        modalMessage.classList.toggle( 'hide' );
        modalMessage.innerHTML = '<h1>Redémarrage du serveur...</h1><p>Le serveur est en cours de redémarrage.<br>Veuillez patienter...</p><p class="loader"></p>';

        const cmd = 'reboot';
        const url = `/admin/cmd.php?cmd=${ encodeURIComponent( cmd ) }&isLocal=${ encodeURIComponent( isLocal ) }&ip=${ encodeURIComponent( ip ) }`;

        fetch( url )
            .then( response => response.text() )
            .then( () => checkServerStatus(ip) );
    } );
}

export function restartService( service, isLocal, ip, desc ) {
    const modalConfirm = modal.querySelector( '.modal-confirm');
    const modalMessage = modal.querySelector( '.modal-content' );

    modal.classList.toggle('hide');
    modalConfirm.classList.toggle('hide');
    modal.querySelector("#confirm").innerHTML = `<p>Le redémarrage du service:<br>${ desc } (${ service })</span>.</p>`;

    cancelButton.addEventListener( 'click', () => {
        modal.classList.toggle('hide');
        modalConfirm.classList.toggle('hide');
    } );

    confirmButton.addEventListener( 'click', () => {

        modalConfirm.classList.add('hide');
        modalMessage.classList.remove('hide');

        modalMessage.innerHTML = `<h1>Redémarrage</h1><p>${ desc } (${ service }</p><p class="loader"/></p>`;
        
        const cmd = 'restart';
        const url = `/admin/cmd.php?cmd=${ encodeURIComponent( cmd ) }&service=${ encodeURIComponent( service ) }&isLocal=${ encodeURIComponent( isLocal ) }&ip=${ encodeURIComponent( ip ) }`;
        fetch( url )
            .then( response => response.text() )
            .then( () => {
                const checkAvailability = setInterval( () => {
                    fetch( window.location.href )
                        .then( response => {
                            if ( response.ok ) {
                                clearInterval( checkAvailability );
                                modalMessage.innerHTML = `<h1>${ service }</h1><p>${ desc } a redémarré.</p>`;
                                setTimeout( closeModal, 5000 );
                                location.reload();
                            }
                        } )
                        .catch( error => console.error( 'Error:', error ) );
                }, 2000 );
            } );
    } );

}

