<?php
require "tools.php";
$icecastAdminUrl = "http://localhost:8000/admin/listclients?mount=/stream";

$username = $ICECAST[0];
$password = $ICECAST[1];

$totalListners = 0;

$peaksFile = "/var/www/html/admin/data/peaks.json";
$peaks = file_exists($peaksFile) ? json_decode(file_get_contents($peaksFile), true) : [];

function formatTime($seconds) {
    if ($seconds >= 86400) { // 1 day = 86400 seconds
        $days = floor($seconds / 86400);
        return "{$days} Day" . ($days > 1 ? "s" : ""); // Add "s" if plural
    } elseif ($seconds >= 3600) { // 1 hour = 3600 seconds
        $hours = floor($seconds / 3600);
        return "{$hours}h";
    } elseif ($seconds >= 60) { // 1 minute = 60 seconds
        $minutes = floor($seconds / 60);
        return "{$minutes}min";
    } else {
        return "{$seconds}s";
    }
}

// Initialize cURL session
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $icecastAdminUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_USERPWD, "$username:$password");
curl_setopt($ch, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);

// Execute cURL and fetch data
$response = curl_exec($ch);
//echo var_dump($response);
if (curl_errno($ch)) {
    die("Error: " . curl_error($ch));
}
curl_close($ch);

// Parse the XML response
$xml = simplexml_load_string($response);
if (!$xml) {
    die("Failed to parse XML.");
}

foreach ($xml->source->listener as $listener) {
    $ip = (string)$listener->IP;
    $ua = (string)$listener->UserAgent;
    $connected =(string)$listener->Connected;
    $id = (string)$listener->ID;
    
    if (! str_contains($listener->UserAgent, "Icecast") and ! str_contains($listener->UserAgent, "mpg123")) {
       $totalListners++;
    }   
}

echo $totalListners;
