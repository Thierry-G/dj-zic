// Configuration
const config = {
    minZoom: 0.5,
    maxZoom: 2.0,
    defaultZoom: 1.0,
    zoomStep: 0.1,
    refreshInterval: 2000,
    masterRange: 100 // meters, for the circle
};

const labelHost = document.getElementById( "label-host" );
const closeTab = document.getElementById( "close" );
let currentZoom = config.defaultZoom;
let fitZoom = 1;
let maxDeviceDistance = 1;
let viewport = null;

// Utility to compute pixels per meter for current zoom
function getPixelsPerMeter( containerHeight, topMargin, bottomMargin, deviceDotHeight, zoom, rangeToShow ) {
    const usableHeight = containerHeight - topMargin - bottomMargin - deviceDotHeight;
    return ( usableHeight / rangeToShow ) * zoom;
}

// Initialize radar
function initRadar() {
    setupEventListeners();
    updateRadarData(); // Initial load
    setInterval( updateRadarData, config.refreshInterval );
}

// Create device element with alternating label positions
function createDeviceElement( deviceData, color, index, pixelsPerMeter, bottomMargin ) {
    const colorsCircle = [ 'rgba(33,150,243,.2)', 'rgba(76,175,80,.2)', 'rgba(156,39,176,.2)', 'rgba(255,82,82,.2)', 'rgba(255,235,59,.2)', 'rgba(0,188,212,.2)' ];
    const element = document.createElement( 'div' );
    element.className = 'device';
    element.id = deviceData.hostname || `device-${ Math.random().toString( 36 ).substr( 2, 5 ) }`;

    // Proportional position: 0m = bottom, max = top
    const positionFromBottom = bottomMargin + deviceData.distance * pixelsPerMeter;
    element.style.position = 'absolute';
    element.style.left = '50%';
    element.style.transform = 'translateX(-50%)';
    element.style.bottom = `${ positionFromBottom }px`;

    const labelPosition = index % 2 === 0 ? 'right' : 'left';

    // Use deviceData.range if you have it, otherwise use deviceData.distance for the circle
    const rangeDiameter = config.masterRange * pixelsPerMeter * 2;
    element.innerHTML = `
        <div class="device-inner">
            <div class="device-range" style="
                width: ${ rangeDiameter }px;
                height: ${ rangeDiameter }px;
                background-color: ${ colorsCircle[ index ] }; 
                border-color: ${ color };
            "></div>
            <div class="device-dot" style="background-color: ${ color };"></div>
            <div class="device-label ${ labelPosition }">
                <p>${ deviceData.hostname || deviceData.type }</p>
                <!-- ${ deviceData.ip || 'N/A' }<br -->
                <span class="device-distance">${ Math.round( deviceData.distance ) }m</span>
            </div>
        </div>
    `;
    return element;
}

// Update radar with data from JSON
function updateRadarData() {
    
    fetch( '/data/distance_data.json' )
        .then( response => response.json() )
        .then( data => {
            // Clear existing devices (keep master)
            document.querySelectorAll( '.device:not(#master)' ).forEach( el => el.remove() );


            // Find max device distance
            const deviceEntries = Object.entries( data.devices );
            maxDeviceDistance = 1;
            deviceEntries.forEach( ( [ , deviceData ] ) => {
                if ( deviceData.distance > maxDeviceDistance ) maxDeviceDistance = deviceData.distance;
            } );
            // Always show at least the master range
            const maxRangeToShow = Math.max( maxDeviceDistance, config.masterRange );

            const containerHeight = document.querySelector( '.radar-container' ).clientHeight;
            const topMargin = 30;
            const bottomMargin = 30;
            const deviceDotHeight = 24;

            // Calculate fitZoom so all devices fit at zoom=1
            fitZoom = 1;
            if ( currentZoom < fitZoom ) currentZoom = fitZoom;

            // Calculate pixelsPerMeter for current zoom and range to show
            const pixelsPerMeter = getPixelsPerMeter(
                containerHeight, topMargin, bottomMargin, deviceDotHeight, currentZoom, maxRangeToShow
            );
            //  
            const colors = [ 'rgb(33,150,243)', 'rgb(76,175,80)', 'rgb(156,39,176)', 'rgb(255,82,82)', 'rgb(255,235,59)', 'rgb(0,188,212)' ];

            deviceEntries.sort( ( [ , a ], [ , b ] ) => a.distance - b.distance );

            deviceEntries.forEach( ( [ hostname, deviceData ], index ) => {
                const color = colors[ index % colors.length ];
                const element = createDeviceElement( {
                    ...deviceData,
                    hostname: hostname
                }, color, index, pixelsPerMeter, bottomMargin );
                document.querySelector( '.radar-viewport' ).appendChild( element );
            } );

            // Set master range circle size and color via JS
            const masterRangeDiameter = config.masterRange * pixelsPerMeter * 2;
            const masterRangeEl = document.querySelector( '#master .device-range' );
            if ( masterRangeEl ) {
                masterRangeEl.style.width = masterRangeDiameter + 'px';
                masterRangeEl.style.height = masterRangeDiameter + 'px';
                masterRangeEl.style.borderColor = '#FFA500';
                masterRangeEl.style.borderWidth = '7px';
                masterRangeEl.style.backgroundColor = 'rgba(110,110,110,.1)';
            }
            labelHost.textContent = data.hostname;
            updateViewportScale( pixelsPerMeter, containerHeight, topMargin, bottomMargin, deviceDotHeight, maxRangeToShow );
        } )
        .catch( error => {
            console.error( "Error loading radar data:", error );
        } );
}

// Update viewport scaling and position
function updateViewportScale( pixelsPerMeter, containerHeight, topMargin, bottomMargin, deviceDotHeight, maxRangeToShow ) {
    // The content height is the max range to show
    const contentHeight = bottomMargin + maxRangeToShow * pixelsPerMeter;
    // Scale and position the viewport
    viewport.style.transform = `scale(1)`;
    // Keep master at bottom, and content at the right place
    if ( contentHeight < containerHeight - topMargin ) {
        viewport.style.bottom = `${ containerHeight - topMargin - contentHeight }px`;
    } else {
        viewport.style.bottom = `0px`;
    }
    document.querySelector( '.scale-indicator' ).textContent = `${ currentZoom.toFixed( 1 ) }x`;
    console.log( currentZoom );
    currentZoom === 1 ? document.getElementById( 'zoom-out' ).disabled = true : document.getElementById( 'zoom-out' ).disabled = false;
    currentZoom === 2 ? document.getElementById( 'zoom-in' ).disabled = true : document.getElementById( 'zoom-in' ).disabled = false;
}

// Zoom functionality
function zoom( direction ) {
    const containerHeight = document.querySelector( '.radar-container' ).clientHeight;
    const topMargin = 30;
    const bottomMargin = 30;
    const deviceDotHeight = 24;

    // Calculate the minimum zoom to fit all devices
    const minZoom = 1;
    const maxZoom = config.maxZoom;

    let newZoom = currentZoom;
    if ( direction === 'in' ) {
        newZoom = Math.min( currentZoom + config.zoomStep, maxZoom );
    } else {
        newZoom = Math.max( currentZoom - config.zoomStep, minZoom );
    }

    if ( newZoom !== currentZoom ) {
        currentZoom = newZoom;
        updateRadarData(); // Re-render with new zoom
    }
}

// Recenter functionality
function recenter() {
    currentZoom = 1;
    updateRadarData();
}

// Event listeners
function setupEventListeners() {
    document.getElementById( 'zoom-in' ).addEventListener( 'click', () => zoom( 'in' ) );
    document.getElementById( 'zoom-out' ).addEventListener( 'click', () => zoom( 'out' ) );
    document.getElementById( 'center' ).addEventListener( 'click', recenter );

    document.querySelector( '.radar-container' ).addEventListener( 'wheel', ( e ) => {
        e.preventDefault();
        zoom( e.deltaY > 0 ? 'out' : 'in' );
    } );
}

// Initialize
document.addEventListener( 'DOMContentLoaded', () => {
    viewport = document.querySelector( '.radar-viewport' );
    setupEventListeners();
    updateRadarData();
    refreshListeners()
    setInterval( refreshListeners, 3000 );
    setInterval(updateRadarData, config.refreshInterval);
} );

function getStreamers( callback ) {
    fetch( "../admin/data/stats.json" )
        .then( response => response.json() )
        .then( data => {
            const current = data.global_current;
            if ( callback ) {
                callback( current );
            }
        } )
        .catch( error => {
            console.error( "Failed to load stats.json:", error );
            if ( callback ) {
                callback( null );
            }
        } );
}

closeTab.addEventListener( 'click', function ( event ) {

    event.preventDefault();
    fetch( "/admin/inc/setSession.php", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "radar=off"
    } )
        .then( resp => resp.text() )
        .then( data => {
            console.log( "Radar: Off" );
            window.opener.postMessage( { radarStatus: "off" }, "*" );
            window.close();
        } )
        .catch( error => {
            console.log( "Rerror:", error )
        } )
} );

// Streamers 
function refreshListeners() {
    getStreamers( function ( count ) {
        const el = document.getElementById( "totalStreamers" );
        if ( count !== null ) {
            el.textContent = count;
        } else {
            el.textContent = "Unavailable";
        }
    } );
}

