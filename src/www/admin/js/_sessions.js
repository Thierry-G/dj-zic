export function setSession( event ) {
    const tabValue = event.target.value; // Get the button's value
    fetch( 'inc/setSession.php', {
        method: 'POST',
        body: new URLSearchParams( { Tab: tabValue } ),
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    } ).then( response => {
        console.log( 'Session set successfully' ); 
        location.reload();
    } ).catch( error => console.error( 'Error:', error ) );
}