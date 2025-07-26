document.addEventListener( 'DOMContentLoaded', function () {

    const step1 = document.getElementById( 'step1' );
    const step2 = document.getElementById( 'step2' );
    const imageInput = document.getElementById( 'imageInput' );
    const selectImageBtn = document.getElementById( 'selectImageBtn' );
    const selectedImage = document.getElementById( 'selectedImage' );
    const imageWrapper = document.getElementById( 'imageWrapper' );
    const cropFrame = document.getElementById( 'cropFrame' );
    const cropDoneBtn = document.getElementById( 'cropDoneBtn' );
    const closeAddPict = document.getElementById( 'closeAddPict' );
    const validateButton = document.getElementById( 'validateButton' );
    const cancelButton = document.getElementById( 'closeButtonB' );
    const cropWait = document.getElementById( 'cropWait' );
    const stream = {
        dj: '',
        src: '',
        live: '',
        id: ''
    }

    let isDragging = false;
    let isResizing = false;
    let startX, startY;
    let startWidth, startHeight, startLeft, startTop;
    let activeHandle = null;
    let imageScale = 1;
    const targetAspect = 9 / 16;

    // Initialize crop frame
    function initCropFrame() {
        const imgWidth = selectedImage.naturalWidth;
        const imgHeight = selectedImage.naturalHeight;
        const displayWidth = selectedImage.clientWidth;
        const displayHeight = selectedImage.clientHeight;

        // Calculate scale factor
        imageScale = imgWidth / displayWidth;

        // Initial frame size (80% of image width, maintaining 9:16)
        const frameWidth = displayWidth * 0.8;
        const frameHeight = frameWidth / targetAspect;

        // Center the frame
        const frameLeft = ( displayWidth - frameWidth ) / 2;
        const frameTop = ( displayHeight - frameHeight ) / 2;

        // Apply styles
        cropFrame.style.width = `${ frameWidth }px`;
        cropFrame.style.height = `${ frameHeight }px`;
        cropFrame.style.left = `${ frameLeft }px`;
        cropFrame.style.top = `${ frameTop }px`;

        // Set wrapper size
        imageWrapper.style.width = `${ displayWidth }px`;
        imageWrapper.style.height = `${ displayHeight }px`;
    }

    // Event listeners for image selection
    selectImageBtn.addEventListener( 'click', () => {
        closeAddPict.classList.toggle( 'hide' );
        if ( document.getElementById( 'iosInfo' ) != undefined ) {
            document.getElementById( 'iosInfo' ).classList.toggle( 'hide' );
        }
        imageInput.click();
    } );

    imageInput.addEventListener( 'change', function ( e ) {
        if ( e.target.files && e.target.files[ 0 ] ) {
            const reader = new FileReader();
            reader.onload = function ( event ) {
                selectedImage.src = event.target.result;
                selectedImage.onload = function () {
                    step1.classList.remove( 'active' );
                    step2.classList.add( 'active' );
                    initCropFrame();
                };
            };
            reader.readAsDataURL( e.target.files[ 0 ] );
        }
    } );

    // Touch/mouse event handling
    function handleStart( e ) {
        e.preventDefault();
        const touch = e.touches ? e.touches[ 0 ] : e;
        startX = touch.clientX;
        startY = touch.clientY;

        if ( e.target.classList.contains( 'resize-handle' ) ) {
            isResizing = true;
            activeHandle = e.target.id;
            const frameRect = cropFrame.getBoundingClientRect();
            startWidth = frameRect.width;
            startHeight = frameRect.height;
            startLeft = parseFloat( cropFrame.style.left );
            startTop = parseFloat( cropFrame.style.top );
        } else if ( e.target === cropFrame ) {
            isDragging = true;
            startLeft = parseFloat( cropFrame.style.left );
            startTop = parseFloat( cropFrame.style.top );
        }
    }

    function handleMove( e ) {
        if ( !isDragging && !isResizing ) return;
        e.preventDefault();

        const touch = e.touches ? e.touches[ 0 ] : e;
        const dx = touch.clientX - startX;
        const dy = touch.clientY - startY;
        const imgRect = selectedImage.getBoundingClientRect();

        if ( isDragging ) {
            // Move frame with boundary checks
            let newLeft = startLeft + dx;
            let newTop = startTop + dy;

            // Keep frame within image bounds
            newLeft = Math.max( 0, Math.min(
                newLeft,
                imgRect.width - parseFloat( cropFrame.style.width )
            ) );
            newTop = Math.max( 0, Math.min(
                newTop,
                imgRect.height - parseFloat( cropFrame.style.height )
            ) );

            cropFrame.style.left = `${ newLeft }px`;
            cropFrame.style.top = `${ newTop }px`;
        }
        else if ( isResizing ) {
            // Resize frame while maintaining aspect ratio
            let newWidth = startWidth;
            let newHeight = startHeight;
            let newLeft = startLeft;
            let newTop = startTop;

            switch ( activeHandle ) {
                case 'resizeHandleBR':
                    newWidth = startWidth + dx;
                    newHeight = newWidth / targetAspect;
                    break;
                case 'resizeHandleBL':
                    newWidth = startWidth - dx;
                    newHeight = newWidth / targetAspect;
                    newLeft = startLeft + dx;
                    break;
                case 'resizeHandleTR':
                    newWidth = startWidth + dx;
                    newHeight = newWidth / targetAspect;
                    newTop = startTop - ( newHeight - startHeight );
                    break;
                case 'resizeHandleTL':
                    newWidth = startWidth - dx;
                    newHeight = newWidth / targetAspect;
                    newLeft = startLeft + dx;
                    newTop = startTop - ( newHeight - startHeight );
                    break;
            }

            // Minimum size and boundary constraints
            const minSize = 50;
            newWidth = Math.max( minSize, newWidth );
            newHeight = Math.max( minSize, newHeight );

            // Adjust position if resizing from left/top
            if ( activeHandle.includes( 'L' ) ) {
                const maxLeft = startLeft + startWidth - minSize;
                newLeft = Math.min( maxLeft, newLeft );
                newLeft = Math.max( 0, newLeft );
                newWidth = startWidth + ( startLeft - newLeft );
                newHeight = newWidth / targetAspect;
            }

            if ( activeHandle.includes( 'T' ) ) {
                const maxTop = startTop + startHeight - minSize;
                newTop = Math.min( maxTop, newTop );
                newTop = Math.max( 0, newTop );
                newHeight = startHeight + ( startTop - newTop );
                newWidth = newHeight * targetAspect;
            }

            // Apply new dimensions
            cropFrame.style.width = `${ newWidth }px`;
            cropFrame.style.height = `${ newHeight }px`;
            cropFrame.style.left = `${ newLeft }px`;
            cropFrame.style.top = `${ newTop }px`;
        }
    }

    function handleEnd() {
        isDragging = false;
        isResizing = false;
        activeHandle = null;
    }

    // Event listeners
    cropFrame.addEventListener( 'mousedown', handleStart );
    cropFrame.addEventListener( 'touchstart', handleStart, { passive: false } );

    document.querySelectorAll( '.resize-handle' ).forEach( handle => {
        handle.addEventListener( 'mousedown', handleStart );
        handle.addEventListener( 'touchstart', handleStart, { passive: false } );
    } );

    document.addEventListener( 'mousemove', handleMove );
    document.addEventListener( 'touchmove', handleMove, { passive: false } );

    document.addEventListener( 'mouseup', handleEnd );
    document.addEventListener( 'touchend', handleEnd );

    cropDoneBtn.addEventListener( 'click', function () {

        const img = selectedImage;
        const frameRect = cropFrame.getBoundingClientRect();
        const imgRect = selectedImage.getBoundingClientRect();

        // Calculate crop coordinates in original image dimensions
        const left = ( frameRect.left - imgRect.left ) * imageScale;
        const top = ( frameRect.top - imgRect.top ) * imageScale;
        const width = frameRect.width * imageScale;
        const height = frameRect.height * imageScale;

        // Create canvas for cropping
        const canvas = document.createElement( 'canvas' );
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext( '2d' );

        ctx.drawImage( img, left, top, width, height, 0, 0, width, height );

        // Convert to data URL
        const croppedImageUrl = canvas.toDataURL( 'image/jpeg' );

        // Set as background
        //document.body.style.backgroundImage = `url(${ croppedImageUrl })`;
        step2.classList.remove( 'active' );

        // Send to server
        saveToServer( croppedImageUrl );
    } );

    function saveToServer( imageData ) {
        // Extract base64 data
        const base64Data = imageData.replace( /^data:image\/jpeg;base64,/, '' );
        const xhr = new XMLHttpRequest();
        xhr.open( 'POST', '/admin/uploadPict.php', true );
        xhr.setRequestHeader( 'Content-Type', 'application/x-www-form-urlencoded' );

        xhr.upload.onprogress = function ( event ) {
            if ( event.lengthComputable ) {
                const percentComplete = ( event.loaded / event.total ) * 100;
                document.getElementById( 'progressBar' ).style.width = percentComplete + '%';
            }
        };

        // Show the progress bar
        document.getElementById( 'progressBarContainer' ).classList.toggle( 'hide' );

        xhr.onload = function () {
            const response = JSON.parse( xhr.responseText );
            if ( xhr.status === 200 ) {
                stream.id = response.id;
                document.getElementById( 'progressBarContainer' ).classList.toggle( 'hide' );
                document.getElementById( 'AddPict' ).style.backgroundColor = 'transparent';
                document.body.style.background = `url('/admin/uploads/${ response.id }.jpg') no-repeat center center`;
                document.body.style.backgroundSize = 'cover';
                document.body.dataset.curr = response.id;
                document.getElementById( 'step3' ).classList.toggle( 'hide' );
                console.log( 'Image saved successfully!' );
            } else {
                console.error( 'Error saving image' );
            }
        };

        xhr.onerror = function () {
            alert( 'Error saving image' );
        };

        xhr.send( `image=${ encodeURIComponent( base64Data ) }` );

    }
    // Handle window resize
    window.addEventListener( 'resize', function () {
        if ( step2.classList.contains( 'active' ) ) {
            initCropFrame();
        }
    } );
    validateButton.addEventListener( 'click', function () {
        cropWait.classList.toggle( 'hide' );
        const cmd = 'validatePict';
        const live = 'true';
        const url = `/admin/cmd.php?cmd=${ encodeURIComponent( cmd ) }&status=${ encodeURIComponent( live ) }&id=${ encodeURIComponent( stream.id ) }`;
        fetch( url )
            .then( response => response.text() )
            .then( () => {

                document.body.style.background = `url('/admin/uploads/${ stream.id }.jpg') no-repeat center center`;
                document.body.style.backgroundSize = 'cover';
                document.getElementById( 'AddPict' ).classList.add( "hide" );

                document.getElementById( 'actionScreen' ).classList.add( "hide" );
                document.querySelector( '.header' ).classList.toggle( "hide" );
                document.querySelector( '.content' ).classList.toggle( "hide" );
                document.querySelector( '.footer' ).classList.toggle( "hide" );
                cropWait.classList.toggle( 'hide' );

            } );
        window.location.reload();
    } );
    cancelButton.addEventListener( 'click', function () {
        cropWait.classList.toggle( 'hide' );
        const cmd = 'delReplace';
        const prev = document.body.dataset.prev;
        const fileId = document.body.dataset.curr;
        alert(`${prev}.\t${fileId}\n`);
        const url = `/admin/cmd.php?cmd=${ encodeURIComponent( cmd ) }&prev=${ encodeURIComponent( prev )}&id=${ encodeURIComponent( fileId ) }`;
        fetch( url )
            .then( response => response.text() )
            .then( () => {
                window.location.reload();
                if ( stream.id == 'default' ) {
                    document.body.style.background = "none";
                } else if ( stream.id != fileId ) {
                    document.body.style.background = `url('/admin/uploads/${ fileId }.jpg') no-repeat center center`;
                    document.body.style.backgroundSize = 'cover';
                } else {
                    document.body.style.background = `url('/admin/uploads/${ stream.id }.jpg') no-repeat center center`;
                    document.body.style.backgroundSize = 'cover';
                }
                cropWait.classList.toggle( 'hide' );
                window.location.reload();
            } );

    } );

} );