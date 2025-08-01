document.addEventListener( 'DOMContentLoaded', function () {

    const sourceUrl = "http://dj.zic:8000/stream";
    const source = document.querySelector( "source" );
    const audio = document.getElementById( 'audio' );
    const canvas = document.getElementById( "visualizer" );
    const canvasCtx = canvas.getContext( "2d" );
    const playStopBtn = document.getElementById( 'playStopBtn' );
    const playIcon = document.getElementById( 'playIcon' );
    const shareBtn = document.getElementById( 'shrareBtn' );
    const currentTimeDisplay = document.getElementById( 'current-time' );
    const modal = document.getElementById( 'modal' );
    const modalContent = document.querySelector( '.modal-content' );
    const title = document.getElementById( 'stream-info' );
    const djName = document.querySelector( '.dj-name' )
    const lang = document.documentElement.lang;

    let audioContext;
    let analyser;
    let mediaSource;
    let animationId = null;
    let isPlaying = false;
    let timeUpdateListenerAdded = false;
    let firstCheck = true;
    let previousDjNameValue = "";
    let currBg = null;

    function initAudioContext() {
        audioContext = new ( window.AudioContext || window.webkitAudioContext )();
        analyser = audioContext.createAnalyser();
        mediaSource = audioContext.createMediaElementSource( audio );

        analyser.fftSize = 256;
        analyser.minDecibels = -90;
        analyser.maxDecibels = -10;
        analyser.smoothingTimeConstant = .95;

        mediaSource.connect( analyser );
        mediaSource.connect( audioContext.destination );
        analyser.connect( audioContext.destination );
    }

    function draw() {
        if ( !analyser ) return;

        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array( bufferLength );
        analyser.getByteFrequencyData( dataArray );

        canvasCtx.clearRect( 0, 0, canvas.width, canvas.height );
        const barWidth = ( canvas.width / bufferLength ) * 2.5;
        let x = 0;

        for ( let i = 0; i < bufferLength; i++ ) {
            const barHeight = ( dataArray[ i ] / 255 ) * canvas.height;
            const y = canvas.height - barHeight;

            const gradient = canvasCtx.createLinearGradient( x, y, x, canvas.height );
            gradient.addColorStop( 0, `rgba(${ Math.min( 255, barHeight + 10 ) }, 247, 247, .5)` );
            gradient.addColorStop( 1, 'rgba(52, 13, 117, 1)' );
            canvasCtx.fillStyle = gradient;
            canvasCtx.fillRect( x, y, barWidth, barHeight );

            x += barWidth + 2;
        }

        animationId = requestAnimationFrame( draw );
    }

    function playBtn() {
        if ( isPlaying ) return;

        if ( !source.getAttribute( "src" ) ) {
            source.setAttribute( "src", sourceUrl );
            audio.load();
        }

        audio.play().then( () => {
            if ( audioContext && audioContext.state === 'suspended' ) {
                audioContext.resume();
            }
            if ( !audioContext ) {
                initAudioContext();
            }
            requestAnimationFrame( draw );
            if ( !timeUpdateListenerAdded ) {
                audio.addEventListener( 'timeupdate', updateCurrentTime );
                timeUpdateListenerAdded = true;
            }
            isPlaying = true;
        } ).catch( handlePlayError );
    }

    function pauseBtn() {
        if ( !isPlaying ) return;

        currentTimeDisplay.textContent = '--:--';
        audio.pause();
        cancelAnimationFrame( animationId );

        audio.removeEventListener( 'timeupdate', updateCurrentTime );
        timeUpdateListenerAdded = false;

        if ( audioContext && audioContext.state !== 'closed' ) {
            audioContext.suspend();
        }

        source.setAttribute( "src", sourceUrl );
        audio.load();

        isPlaying = false;
    }

    function handlePlayStop( e ) {
        e.preventDefault();
        if ( mode == 'pause' ) {
            playStopBtn.style.backgroundColor = 'darkgrey';
            // alert(document.querySelector( '#playIcon path' ));
            // document.querySelector( '#playIcon path' ).setAttribute( 'fill', 'darkslategrey' );
        } else if ( mode == 'start' ) {
            if ( audio.paused ) {
                updateUI( 'play' );
                playBtn();
            } else {
                updateUI( 'stop' );
                pauseBtn();
            }
        }
    }

    function updateCurrentTime() {
        const hours = Math.floor( audio.currentTime / 3600 );
        const minutes = Math.floor( ( audio.currentTime % 3600 ) / 60 )
            .toString()
            .padStart( 2, '0' );
        const seconds = Math.floor( audio.currentTime % 60 )
            .toString()
            .padStart( 2, '0' );

        currentTimeDisplay.textContent = hours > 0
            ? `${ hours }:${ minutes }:${ seconds }`
            : `${ minutes }:${ seconds }`;
    }

    function handlePlayError( error ) {
        console.error( 'Play failed:', error );
        if ( error.name === 'NotAllowedError' ) {
            console.log( 'Playback requires user interaction first' );
        }
    }

    function updateUI( status ) {

        if ( mode == 'pause' ) {
            playStopBtn.style.backgroundColor = 'darkgrey';
            document.getElementById( 'simpleMsg' ).classList.remove( 'hide' )
            document.getElementById( 'modal' ).classList.add( 'hide' )
        }
        else {
            document.getElementById( 'simpleMsg' ).classList.add( 'hide' )
            if ( status === 'stop' ) {
                playIcon.setAttribute( 'd', 'M16 12 L56 32 L16 52 Z' );
                playStopBtn.style.backgroundColor = 'red';
                clearCanvas();
            } else if ( status === 'play' ) {
                title.style.display = 'none';
                playIcon.setAttribute( 'd', 'M 16 16 L 48 16 L 48 48 L 16 48 L 16 16 Z' );
                playStopBtn.style.backgroundColor = 'rgb(52, 13, 117)';
            }
        }

    }

    function clearCanvas() {
        canvasCtx.clearRect( 0, 0, canvas.width, canvas.height );
    }

    async function checkStreamStatus() {
        try {
            const response = await fetch( '/data/status.json' );
            if ( !response.ok ) {
                throw new Error( 'Network response was not ok' );
            }
            const data = await response.json();

            updateStreamInfo( data[ 'stream' ] );
            streamStatus = data[ 'sound' ];
            mode = data[ 'stream' ][ 'status' ];

            const djName = document.querySelector( '.dj-name' )

            switch ( mode ) {
                case 'stop':
                    simpleMsg.classList.add( 'active' );
                    simpleMsg.classList.remove( 'hide' );
                    document.querySelector('.off').classList.remove('hide');
                    document.querySelector('.soon').classList.add('hide');
                    djName.textContent = lang == 'fr' ? "Les serveurs sont hors ligne." : "Servers are off line. ";

                    playStopBtn.style.color = 'darkslategrey';
                    playStopBtn.disabled = true;
                    playStopBtn.style.opacity = .7;
                    break;

                case 'start':
                    simpleMsg.classList.remove( 'active' );
                    simpleMsg.classList.add( 'hide' );
                    playStopBtn.style.backgroundColor = 'red';
                    document.getElementById( 'simpleMsg' ).classList.add( 'hide' );
                    djName.textContent = data[ 'stream' ][ 'dj' ];
                    if ( streamStatus === 'silent' ) {
                        modalContent.innerHTML = firstCheck ? '<h1>Merci de patienter</h1><p>La diffusion du stream débute bientôt.</p>' : '<h1>Merci de patienter</h1><p>La diffusion du stream est interrompue et reprendra automatiquement.</p>';
                        modal.style.display = 'flex';
                        currentTimeDisplay.textContent = '--:--';
                        clearCanvas();
                        audio.removeEventListener( 'timeupdate', updateCurrentTime );
                        timeUpdateListenerAdded = false;
                    } else {
                        playStopBtn.disabled = false;
                        playStopBtn.style.opacity = 1;
                        modal.style.display = 'none';
                        if ( !timeUpdateListenerAdded ) {
                            audio.addEventListener( 'timeupdate', updateCurrentTime );
                            timeUpdateListenerAdded = true;
                        }
                        if ( isPlaying ) {
                            updateUI( 'play' );
                        }
                        firstCheck = true;
                    }
                    break;
                case 'pause':
                    simpleMsg.classList.add( 'active' );
                    simpleMsg.classList.remove( 'hide' );
                    document.querySelector('.off').classList.add('hide');
                    document.querySelector('.soon').classList.remove('hide');
                    djName.textContent = lang == 'fr' ? "Le stream commence bientôt" : "The live stream will soon begin.";

                    playStopBtn.style.backgroundColor = 'darkgrey';
                    playStopBtn.style.color = 'darkslategrey';
                    playStopBtn.disabled = true;
                    playStopBtn.style.opacity = .7;
                    break;
            }

        } catch ( error ) {
            console.error( 'Failed to fetch stream status:', error );
            clearCanvas();
            updateUI( 'stop' );
            modalContent.innerHTML = '<h1>Merci de patienter</h1><p>La diffusion du stream est interrompue.</p>';
            title.querySelector( '.arrow-paragraph' ).innerHTML = "Reprendre l'écoute";
            modal.style.display = 'flex';
            title.style.display = 'flex';
            location.reload;
        }
    }

    function setBg( streamInfo ) {
        const style = document.createElement( 'style' );
        style.innerHTML = ` .bg { background: url('/admin/uploads/${ streamInfo.src }') no-repeat center center; background-size: cover !important; }`;
        document.head.appendChild( style );
        document.body.classList.add( 'bg' );
    }

    function updateStreamInfo( streamInfo ) {

        const djNameValue = streamInfo.dj.replace( /\n/g, "<br />" );
        const normalizedStreamInfo = streamInfo.dj; // Raw stream info with \n

        // Check if streamInfo.dj has changed before updating
        if ( normalizedStreamInfo !== previousDjNameValue && !djName.classList.contains( 'change' ) ) {
            djName.innerHTML = djNameValue;

            djName.classList.add( 'change' );
            djName.addEventListener( 'transitionend', () => {
                djName.classList.remove( 'change' );
                previousDjNameValue = normalizedStreamInfo; // ✅ Update stored previous value
            }, { once: true } );
        }

        if ( currBg === null && streamInfo.id !== 'default' ) {
            setBg( streamInfo );
            currBg = streamInfo.id;
        }

        if ( currBg != streamInfo.id ) {
            const isStyled = document.head.querySelector( "style" );
            const hasBg = document.body.classList.contains( 'bg' );
            if ( streamInfo.live === 'true' ) {
                if ( isStyled ) {
                    isStyled.remove();
                }
                setBg( streamInfo );
                currBg = streamInfo.id;
            }
            else if ( streamInfo.live === 'false' ) {
                if ( isStyled ) {
                    isStyled.remove();
                }
                if ( hasBg ) {
                    document.body.classList.remove( 'bg' );
                }
                currBg = streamInfo.id;
            }
        }
    }

    playStopBtn.addEventListener( 'click', handlePlayStop );
    shareBtn.addEventListener( 'click', () => {
        document.getElementById( 'help' ).classList.toggle( 'open' );
        document.getElementById( 'streamer' ).classList.toggle( 'dW' );
        shareBtn.classList.toggle( 'open' );
    } );

    const stepsContainer = document.querySelector( '.steps' ); // The scrolling container
    const steps = document.querySelectorAll( '.step' ); // All slides
    const dots = document.querySelectorAll( '.dot' ); // All dots

    function updateDots( activeIndex ) {
        dots.forEach( ( dot, i ) => {
            dot.classList.toggle( 'active', i === activeIndex );
        } );
    }

    function getCurrentIndex() {
        const containerScrollPosition = stepsContainer.scrollLeft;
        const stepWidth = stepsContainer.offsetWidth;
        return Math.round( containerScrollPosition / stepWidth );
    }

    // Swipe handling and updating dots dynamically
    stepsContainer.addEventListener( 'scroll', () => {
        const currentIndex = getCurrentIndex();
        updateDots( currentIndex );
    } );

    dots.forEach( ( dot, i ) => {
        dot.addEventListener( 'click', ( e ) => {
            e.preventDefault(); // Prevent default anchor behavior
            steps[ i ].scrollIntoView( { behavior: 'smooth', block: 'nearest' } );
            updateDots( i );
        } );
    } );

    checkStreamStatus();
    setInterval( checkStreamStatus, 500 );

} );
