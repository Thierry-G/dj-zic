import { ALERT, H1, BG, ALERT_BORDER } from './_Colors.js';


export const soundButton = document.getElementById( 'cutSound' );

export function updateSoundState(lang) {
    
    let cmd;
    isSoundOn = !isSoundOn;
    if ( isSoundOn ) {
        // Sound is on - show waves and animations
        leftWave1.style.display = 'block';
        leftWave2.style.display = 'block';
        rightWave1.style.display = 'block';
        rightWave2.style.display = 'block';
        speaker.style.fill = 'rgb(21, 21, 21)';
        svgContainer.classList.add( 'sound-on' );
        soundButton.textContent = lang == 'fr' ? 'Et, je coupe le son... ' : '...And, I turn the sound off !';
        soundButton.style.backgroundColor = H1;
        soundButton.style.color = BG;
        soundButton.style.fontWeight = "normal";
        cmd = 'unmute';
    } else {
        // Sound is off - hide waves and animations
        leftWave1.style.display = 'none';
        leftWave2.style.display = 'none';
        rightWave1.style.display = 'none';
        rightWave2.style.display = 'none';
        speaker.style.fill = 'rgb(150, 150, 150)';
        svgContainer.classList.remove( 'sound-on' );
        soundButton.textContent = lang == 'fr' ? '...et, Je remets le son !' : '...And, I turn the sound on !';
        soundButton.style.backgroundColor = ALERT;
        soundButton.style.color = BG;
        soundButton.style.Border = `2px solid ${ALERT_BORDER} !important`;
        soundButton.style.fontWeight = "bold";
        cmd = 'mute';
    }

    const url = `/admin/cmd.php?cmd=${ encodeURIComponent( cmd ) } `;
    fetch( url )
        .then( response => response.text() )
        .then( () => {
            cutSound.value = cmd;
            cutSound.classList.toggle( 'off' );
        } )
        .catch( error => console.error( 'Error:', error ) );
}