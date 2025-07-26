import { ALERT, H1, BG, ALERT_BORDER } from './_Colors.js';

export function icecastDetails() {
    const streamers = document.getElementById( 'streamers' );
    const icecast = document.querySelector( '.icecast' );
    icecast.classList.toggle( 'hide' );
    icecast.classList.toggle( 'rolled' )
    document.getElementById( 'totalStreamers' ).classList.toggle( 'hide' )
    streamers.classList.toggle( 'rolled' );
    icecast.classList.contains('rolled') ?  (streamers.style.color = BG, streamers.style.backgroundColor = H1) :  (streamers.style.color = H1, streamers.style.backgroundColor = BG)
   
    streamers.style.borderRadius = '50%';
    console.log(streamers)
}