<?php
session_start();
if (isset($_SESSION['auth'])) {
    if ($_SESSION['auth'] === true) {
        // User is authenticated
    }
} else {
    header('Location: login.php');
    exit;
}
require_once 'inc/tools.php';
$dataStream = getFileJsonData($STREAM);


header('Content-Type: application/json');

if (isset($_POST['image'])) {
    $imageData = $_POST['image'];
    $decodedImage = base64_decode($imageData);

    $fileId = uniqid();
    $fileName = "$fileId.jpg";
    $filePath = "/var/www/html/admin/uploads/$fileName";
  
    if (file_put_contents($filePath, $decodedImage)) {
        // Generate CSS class
        $className = pathinfo($fileName, PATHINFO_FILENAME);

        $dataStream['stream']['id'] = $fileId;
        $dataStream['stream']['src'] = $fileName;
        $dataStream['stream']['live'] = 'validation';
      
        saveJsonData($dataStream, $STREAM);

        // Track the uploaded files
        $logFilePath = 'uploads/upload_log.json';
        $logData = [];
        if (file_exists($logFilePath)) {
            $logData = json_decode(file_get_contents($logFilePath), true);
        }
        $logData[] = [
            'file' => $fileName,
            'date' => date('Y-m-d H:i:s')
        ];
        file_put_contents($logFilePath, json_encode($logData));
        $_SESSION['upBg'] = $fileId;
        echo json_encode(['success' => true, 'message' => 'Image uploaded successfully!', 'id' => $fileId]);
    } 
} else {
    echo json_encode(['success' => false, 'message' => 'No image data received.']);
}
