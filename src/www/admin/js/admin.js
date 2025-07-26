import { icecastDetails } from './_icecastPanel.js';
import { StreamSingleton } from './_Stream.js';
import { drawChart } from './_doughnutChart.js';
import { setSession } from './_sessions.js';
import { setAlert } from './_alerts.js';
import { maxChars, verifyField, showHideDjName, showHideDjPict, addPictClose } from './_changeName.js';
import { UiVignettes, deleteBg, setCurrentBg } from './_manage.js';
import { toggleServiceList, restartService, rebootServer } from './_services.js';
import { soundButton, updateSoundState } from './_party.js';
import { message } from './_lang.js';
import { StreamController } from './_startStop.js';

window.globalStreamInstance = null;
window.drawChart = drawChart;
window.setSession = setSession;
window.restartService = restartService;
window.toggleServiceList = toggleServiceList;
window.restartService = restartService;
window.rebootServer = rebootServer;
window.UiVignettes = UiVignettes;
window.deleteBg = deleteBg;
window.setCurrentBg = setCurrentBg;
window.verifyField = verifyField;
window.showHideDjName = showHideDjName;
window.StreamController = StreamController;

window.isSoundOn = false;

( async () => {
    window.globalStreamInstance = await StreamSingleton.getInsance();
} )();

export const lang = document.documentElement.lang;
/**
 *  Controlers
 */
const modal = document.getElementById( 'modal' );
const modalMessage = modal.querySelector( '.modal-content' );
const AddPict = document.getElementById( 'AddPict' );
const ManagePict = document.getElementById( 'ManagePict' );
const closePictMgt = document.getElementById( 'closePictMgt' );
const closeButtonA = document.getElementById( 'closeButtonA' );
const closeButtonB = document.getElementById( 'closeButtonB' );
const djNameMenu = document.getElementById( "djNameMenu" );
const djNameBtn = document.getElementById( 'djNameBtn' );
const djNameClose = document.getElementById( 'djNameClose' );
const djNameInput = document.getElementById( 'djNameInput' );
const changeName = document.getElementById( 'ActionChangeDjName' );
const djNameError = djNameMenu.querySelector( '#djNameError' );
const charCount = document.getElementById( "charCount" );
const djPict = document.getElementById( 'djPict' );
const djPictBtn = document.getElementById( 'djPictBtn' );
const djPictClose = document.getElementById( 'djPictClose' );
const closeAddPict = document.getElementById( 'closeAddPict' );
const pictMgt = document.getElementById( 'pictMgt' );
const tabStream = document.getElementById( 'stream' );
const tabSystem = document.getElementById( 'system' );
const tabParty = document.getElementById( 'party' );
const radarSwitch = document.getElementById( 'switchToggle' );
const quit = document.getElementById( 'endParty' );
const actionUi = document.getElementById( 'actionScreen' );
const streamers = document.getElementById( 'streamers' ); 
const rebootAll = document.getElementById( 'rebootAll' );

updateSoundState( lang );


document.addEventListener( 'DOMContentLoaded', async () => {
    // First, ensure StreamSingleton is initialized
    window.globalStreamInstance = await StreamSingleton.getInstance();
    
    // Then create and initialize StreamController
    const streamController = await new StreamController().init();
    
    // Add click handler
    document.getElementById( 'eventStart' ).addEventListener( 'click', async ( event ) => {
        event.preventDefault();
        await streamController.getMode();
    } );


    window.drawChart();

    djNameBtn.addEventListener( 'click', ( event ) => {
        event.preventDefault();
        djNameBtn.classList.toggle( 'hide' );
        showHideDjName();
    } );

    djNameClose.addEventListener( 'click', function ( event ) {
        event.preventDefault();
        djNameBtn.classList.toggle( 'hide' );
        showHideDjName();
    } );

    djPictBtn.addEventListener( 'click', function ( event ) {
        event.preventDefault();
        showHideDjPict()
    } );

    djPictClose.addEventListener( 'click', function ( event ) {
        event.preventDefault();
        showHideDjPict()
    } );

    djNameError.addEventListener( 'click', function ( event ) {
        event.preventDefault();
        djNameError.classList.toggle( 'hide' )
    } );

    changeName.addEventListener( 'click', function ( event ) {
        event.preventDefault();

        djNameBtn.classList.add( 'hide' );

        let error = verifyField( djNameInput.value );

        if ( djNameInput.value == window.globalStreamInstance.streamInfo.dj ) {
            error = message[ lang ].noModifError;
        }

        if ( error ) {
            setAlert( djNameInput, djNameError, changeName, error );
            return;
        }

        const cmd = 'changeDjName';
        const djNameValue = djNameInput.value.replace( /\n/g, "[NEWLINE]" );
        const url = `/admin/cmd.php?cmd=${ encodeURIComponent( cmd ) }&djName=${ encodeURIComponent( djNameValue ) }`;
        changeName.disabled = true;
        changeName.classList.toggle( 'hide' );
        changeName.nextElementSibling.classList.toggle( 'hide' );
        fetch( url )
            .then( response => response.text() )
            .then( () => {

                setTimeout( () => {
                    changeName.classList.toggle( 'hide' );
                    changeName.nextElementSibling.classList.toggle( 'hide' );
                    djNameMenu.querySelector( 'h2' ).innerHTML = djNameInput.value;
                    djNameBtn.classList.toggle( 'hide' );
                    showHideDjName();
                }, 1000 );

                window.globalStreamInstance.streamInfo.dj = djNameInput.value;
            }
            );
    } );

    djNameInput.addEventListener( 'input', function ( event ) {
        event.preventDefault();

        if ( !djNameError.classList.contains( 'hide' ) ) {
            djNameError.classList.add( 'hide' )
        };

        const remaining = maxChars - this.value.length;
        charCount.textContent = `${ remaining }`;

        if ( remaining <= 0 ) {
            this.value = this.value.substring( 0, maxChars );
            changeName.disabled = true;
            const msg = `${ message[ lang ].maxCharReached } ${ maxChars }.`;
            setAlert( djNameInput, djNameError, changeName, msg );
        } else {
            changeName.disabled = false;
        }

        this.style.height = "auto";
        this.style.height = `${ this.scrollHeight }px`;
    } );

    djPict.addEventListener( 'click', function ( event ) {
        event.preventDefault();
        document.querySelector( '.header' ).classList.toggle( "hide" );
        document.querySelector( '.content' ).classList.toggle( "hide" );
        document.querySelector( '.footer' ).classList.toggle( "hide" );
        actionUi.classList.toggle( 'hide' );
        AddPict.classList.toggle( 'hide' );
    } );

    closeButtonA.addEventListener( 'click', function ( event ) {
        event.preventDefault();
        addPictClose();
        showHideDjPict();
        location.reload()
    } );

    closeButtonB.addEventListener( 'click', function ( event ) {
        event.preventDefault();
        addPictClose();
        showHideDjPict();
        location.reload()
    } );

    closeAddPict.addEventListener( 'click', function ( event ) {
        event.preventDefault();
        addPictClose();
        showHideDjPict();
    } );

    document.addEventListener( 'DOMContentLoaded', function () {
        UiVignettes();
    } );

    pictMgt.addEventListener( 'click', function ( event ) {
        event.preventDefault();

        document.querySelector( '.header' ).classList.toggle( "hide" );
        document.querySelector( '.content' ).classList.toggle( "hide" );
        document.querySelector( '.footer' ).classList.toggle( "hide" );
        actionUi.classList.toggle( 'hide' );
        ManagePict.classList.toggle( 'hide' );
    } );

    closePictMgt.addEventListener( 'click', function ( event ) {
        event.preventDefault();
        document.querySelector( '.header' ).classList.toggle( "hide" );
        document.querySelector( '.content' ).classList.toggle( "hide" );
        document.querySelector( '.footer' ).classList.toggle( "hide" );
        actionUi.classList.toggle( 'hide' );
        ManagePict.classList.toggle( 'hide' );
        showHideDjPict();
        location.reload()
    } );

    soundButton.addEventListener( 'click', function () {
        updateSoundState( lang );
    } );

    tabStream.addEventListener( 'click', setSession );
    tabSystem.addEventListener( 'click', setSession );
    tabParty.addEventListener( 'click', setSession );

    quit.addEventListener( 'click', function ( event ) {
        event.preventDefault();
        
        if (!confirm(message[ lang ].shutdownAll)) {
            return; 
        }
        const cmd = 'allOff';
        const url = `/admin/cmd.php?cmd=${ encodeURIComponent( cmd ) }`;
        this.disabled = true;

        fetch( url )
            .then( response => response.text() )
            .then( () => {
                const checkAvailability = setInterval( () => {
                    fetch( window.location.href )
                        .then( response => {
                            if ( !response.ok ) {
                                modal.classList.toggle( 'hide' );
                                modalMessage.innerHTML = `<h1>${ message[ lang ].unplug }</h1>`;
                                modalMessage.classList.toggle( 'hide' );
                                clearInterval( checkAvailability );
                            }
                        } )
                        .catch( error => {
                            modal.classList.toggle( 'hide' );
                            modalMessage.innerHTML = `<h1>${ message[ lang ].unplug }</h1>`;
                            modalMessage.classList.toggle( 'hide' );
                            console.error( 'Error:', error );
                            clearInterval( checkAvailability );
                            return;
                        } );
                }, 2000 );
            } );
    } );

    rebootAll.addEventListener( 'click', function ( event ) {
        event.preventDefault();
        if (!confirm(message[ lang ].rebootAll)) {
            return; 
        }
        const cmd = 'rebootAll';
        const url = `/admin/cmd.php?cmd=${ encodeURIComponent( cmd ) }`;
        fetch( url )
            .then( response => response.text() )
            .then( text => {
            }
            );
    } );

    streamers.addEventListener( 'click', function ( event ) {
        event.preventDefault();
        
        icecastDetails();
        

    } )

    let radarTab = null;

    radarSwitch.addEventListener( 'change', function () {
        const message = document.getElementById( 'switchMessage' );
        if ( this.checked ) {
            fetch( "/admin/inc/setSession.php", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: "radar=on"
            } )
                .then( response => response.text() )
                .then( data => {
                    // Optionally handle response
                } )
                .catch( error => {
                    console.log( "Rerror:", error )
                } );
            radarTab = window.open( 'radar.php', '_blank' ); // Save reference
            message.textContent = lang == 'fr' ? "Le radar est dans un nouvel onglet.<br>Fermer l'onglet pour réactiver ce contrôle." : "Radar view is on a new tab.<br>Close the tab to reactivate this control.";
        } else {
            fetch( "/admin/inc/setSession.php", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: "radar=off"
            } )
                .then( response => response.text() )
                .then( data => {
                    // Optionally handle response
                } )
                .catch( error => {
                    console.log( "Rerror:", error )
                } );
            if ( radarTab && !radarTab.closed ) {
                radarTab.close(); // Close the tab if it's open
                radarTab = null;
            }
        }
    } );

    window.addEventListener( "message", ( event ) => {
        if ( event.data.radarStatus === "off" ) {
            console.log( "Radar tab has been closed. Session should be OFF." );

            // Optionally re-validate the session state via fetch
            fetch( "/admin/inc/setSession.php", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: "radar"
            } )
                .then( res => res.text() )
                .then( data => {
                    if ( data === "off" ) {
                        document.getElementById( 'switchToggle' ).checked = false;
                        document.getElementById( 'switchMessage' ).textContent = lang == 'fr' ? "Activer le radar ouvrira un nouvel onglet." : "Radar acrivation opens a new tab.";
                    }
                } );
        }
    } );


} );


function getStreamers( callback ) {
    fetch( "../admin/data/stats.json" )
        .then( response => response.json() )
        .then( data => {
            // Update total streamers display
            const totalStreamers = data.global_current || 0;
            document.getElementById( 'totalStreamers' ).textContent = totalStreamers;

            if ( data.servers ) {
                const streamers = Object.entries( data.servers );
                if ( streamers.length > 0 ) {
                    document.querySelector( '.icecast' ).classList.remove( 'hide' );
                } else {
                    document.querySelector( '.icecast' ).classList.add( 'hide' );
                }
            }

            if ( callback ) callback();
        } )
        .catch( error => {
            console.error( 'Error fetching streamers:', error );
            document.getElementById( 'totalStreamers' ).textContent = '--';
            document.querySelector( '.icecast' ).classList.add( 'hide' );
        } );
}

// Initial load
getStreamers();

// Refresh every 2 seconds
setInterval( () => getStreamers(), 2000 );
