<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mobile Device Frame</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f0f0f0;
        }
        .mobile-frame {
            position: relative;
            width: 430px; /* Adjust to your preferred device width */
            height: 932px; /* Adjust to your preferred device height */
            border: 16px solid black; /* Mimics the mobile device bezel */
            border-radius: 30px; /* Rounded corners for a phone-like appearance */
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5); /* Adds depth */
            overflow: hidden; /* Ensures content stays within the frame */
            background-color: #ffffff;
        }
        .screen {
            width: 100%;
            height: 100%;
            border: none;
        }
    </style>
</head>
<body>
    <div class="mobile-frame">
        <iframe src="/" class="screen"></iframe> <!-- Replace with your website's URL -->
    </div>
</body>
</html>