<?php
$CONFIG = '/var/www/html/admin/data/config.json';
$STATUS = '/var/www/html/data/status.json';
$STREAM = '/var/www/html/data/stream.json';
$ICECAST = ['XXXXXX', 'XXXXXX'];
$WIFI = 'XXXXXX';
$WEBADMIN = ['XXXXXX', 'XXXXXX'];

function getUSer()
{
    return 'thierry';
}

function setBgurl($img)
{
    return "background-image: url($img);background-repeat: no-repeat;background-size: cover;";
}

function formatDateTime($dateTimeString)
{
    // Array of French month names
    $months = [
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre"
    ];

    // Parse the date-time string
    $dateTime = new DateTime($dateTimeString);

    // Extract the day, month, year, hour, and minute
    $day = $dateTime->format('d');
    $month = $months[(int)$dateTime->format('m') - 1];
    $year = $dateTime->format('Y');
    $hours = $dateTime->format('H');
    $minutes = $dateTime->format('i');

    // Format the result
    return "<span class=\"date\">{$day} {$month} {$year}</span><br><span class=\"time\">{$hours}h{$minutes}</span>";
}

function getFolderSize($folderPath)
{
    $totalSize = 0;

    // Open the directory
    $files = scandir($folderPath);

    foreach ($files as $file) {
        // Skip current and parent directory entries
        if ($file === '.' || $file === '..') {
            continue;
        }

        $filePath = $folderPath . DIRECTORY_SEPARATOR . $file;

        // If it's a directory, recursively calculate its size
        if (is_dir($filePath)) {
            $totalSize += getFolderSize($filePath);
        } else {
            // If it's a file, add its size
            $totalSize += filesize($filePath);
        }
    }

    return $totalSize;
}

function getDiskTotalSize($diskPath)
{
    return disk_total_space($diskPath);
}

function getSshJsonData($ip)
{
    $user = getUser();
    $command    = "ssh $user@$ip cat /var/www/html/data/status.json";
    $output     = [];
    $return_var = 0;
    exec($command, $output, $return_var);
    $json = implode("\n", $output);
    $data = json_decode($json, true);
    return $data;
}
function getUrlJsonData($ip)
{
    $url = "http://$ip/data/status.json";

    // Initialize a cURL session
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $response = curl_exec($ch);

    // Check for errors
    if (curl_errno($ch)) {
        curl_close($ch);
        return getSshJsonData($ip);
    }

    curl_close($ch);
    $data = json_decode($response, true);
    return $data;
}


function ping($target)
{
    $cmd_result = shell_exec("ping -c 1 -w 1 $target");
    if (preg_match('/0 received/i',  $cmd_result)) {
        return false;
    } else {
        return true;
    }
}

function getFileJsonData($jsonFilePath)
{
    $json = file_get_contents($jsonFilePath);
    $data = json_decode($json, true);
    return $data;
}

function saveJsonData($data, $file)
{
    $updated = json_encode($data);
    file_put_contents($file, $updated);
}

function setStreamValue($key, $value, $file)
{
    $data = json_decode(file_get_contents($file), true);
    $data['stream'][$key] = $value;
    $updated = json_encode($data);
    file_put_contents($file, $updated);
}

function getWlan0Ip()
{
    $wlan = 'wlan0';
    $ip = shell_exec("ip addr show $wlan | grep 'inet ' | awk '{print $2}' | cut -d/ -f1");
    $ip = trim($ip);
    return $ip;
}

function detectiOS()
{
    $userAgent = $_SERVER['HTTP_USER_AGENT'];
    return preg_match('/iPhone|iPad|iPod/i', $userAgent);
}
