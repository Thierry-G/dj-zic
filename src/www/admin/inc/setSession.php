<?php
session_start();

function execCmd($cmd) {
    $output = [];
    exec($cmd, $output, $status);
    // var_dump($output); // You probably don't want this in production
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['Tab'])) {
    $_SESSION['GUI'] = ['Tab' => $_POST['Tab']];
} elseif ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['radar'])) {
    switch ($_POST['radar']) {
        case 'on':
            $_SESSION['Radar'] = 'on';
            $command = 'systemctl start djZic-wifiRadar';
            execCmd($command);
            echo 'on';
            break;
        case 'off':
            $_SESSION['Radar'] = 'off';
            $command = 'systemctl stop djZic-wifiRadar';
            execCmd($command);
            echo 'off';
            break;
        default:
            echo isset($_SESSION['Radar']) ? $_SESSION['Radar'] : 'off';
            break;
    }
}