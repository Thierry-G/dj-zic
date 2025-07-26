<?php
session_start();
require_once 'inc/tools.php';

$streamInfo = getFileJsonData($STREAM);
$curr = $streamInfo['stream']['src'];

if (!isset($_SESSION['curr_src'])) {
    $_SESSION['curr_src'] = $curr;
    $_SESSION['prev_src'] = null;
} elseif ($_SESSION['curr_src'] !== $curr) {
    // Update previous only if stream source changed
    $_SESSION['prev_src'] = $_SESSION['curr_src'];
    $_SESSION['curr_src'] = $curr;
}

$config = getFileJsonData($CONFIG);
$servers = $config['servers'];
$host = getWlan0Ip();

function getKey()
{
    $user = getUser();
    return "/home/$user/.ssh/id_rsa_djzic";
}

function scpUploads()
{
    global $remotes;
    $path   = "/var/www/html/admin/uploads/";
    $sshKey = getKey();
    $user   = getUser();

    // Get list of local JPGs
    $localFiles = array_map('basename', glob($path . "*.jpg"));
    $localMap   = array_flip($localFiles);

    foreach ($remotes as $ip) {
        echo "$ip<br>\n";

        // Get list of remote JPGs
        $remoteListCmd = "ssh -i $sshKey $user@$ip \"ls $path*.jpg 2>/dev/null | xargs -n1 basename\"";
        $remoteFiles = explode("\n", trim(shell_exec($remoteListCmd)));

        $uploads = [];

        foreach ($remoteFiles as $remoteFile) {
            // If file is on remote but not local: delete
            if (!isset($localMap[$remoteFile])) {
                $deleteCmd = "ssh -i $sshKey $user@$ip \"rm -f '$path$remoteFile'\"";
                echo "Deleting: $deleteCmd<br>\n";
                shell_exec($deleteCmd);
            }
        }

        // Check for mismatched or missing files
        foreach ($localFiles as $base) {
            $file       = $path . $base;
            $localSize  = filesize($file);
            $sizeCmd    = "ssh -i $sshKey $user@$ip stat -c%s $path$base 2>/dev/null || echo 0";
            $remoteSize = trim(shell_exec($sizeCmd));

            if ((int)$localSize !== (int)$remoteSize) {
                $uploads[] = "sudo scp -i $sshKey \"$file\" $user@$ip:\"$path$base\"";
            }
        }

        // Add the JSON files once
        $uploads[] = "sudo scp -i $sshKey \"$path/upload_log.json\" $user@$ip:\"$path/upload_log.json\"";
        $uploads[] = "sudo scp -i $sshKey \"/var/www/html/data/stream.json\" $user@$ip:\"/var/www/html/data/stream.json\"";

        // Execute all uploads per IP
        $fullCommand = implode(" && ", $uploads);
        echo "Uploading:<br>$fullCommand<br>\n";
        exec($fullCommand, $output, $status);
        echo "Status for $ip: $status<br>\n";
    }
}

function sshCmd($cmd)
{
    $sshKey = getKey();
    $user = getUser();
    $rcmd = "sudo -u $user /usr/bin/ssh -i $sshKey $user@$cmd";
    $output = [];
    $return_var = 0;
    exec($rcmd, $output, $status);

    if ($status === 0) {
        echo "\n$rcmd completed successfully.\n";
        echo '<br>';
    } else {
        echo "\n$rcmd failed. Status code: $status\n";
        echo '<br>';
    }
}

function setServiceDown($service, $file)
{
    $status = getFileJsonData($file);
    $status["services"][$service] = 0;
    $json = json_encode($status, JSON_PRETTY_PRINT);
    file_put_contents($file, $json);
}

if (isset($_GET['cmd'])) {
    global $servers;
    $remotes = array_map(
        function ($subArray) {
            return $subArray['ip'];
        },
        array_filter($servers, function ($subArray) use ($host) {
            return $subArray['ip'] !== $host && ping($subArray['ip']);
        })
    );

    switch ($_GET['cmd']) {

        case 'allOff':
            $command = 'sudo systemctl poweroff';
            if (count($remotes) > 0) {
                foreach ($remotes as $key => $value) {
                    sshCmd("$value" . " $command");
                }
            }
            $output = [];
            $return_var = 0;
            exec($command, $output, $return_var);
            echo "Done $command";
            break;

        case 'mute':
            $command = 'sudo amixer -D default set PCM mute';
            $output = [];
            $return_var = 0;
            exec($command, $output, $return_var);

            if (count($remotes) > 0) {
                foreach ($remotes as $key => $value) {
                    sshCmd("$value" . " $command");
                }
            }
            echo "Done $command";
            break;

        case 'unmute':
            $command = 'sudo amixer -D default set PCM unmute';
            $output = [];
            $return_var = 0;
            exec($command, $output, $return_var);
            if (count($remotes) > 0) {
                foreach ($remotes as $key => $value) {
                    sshCmd("$value" . " $command");
                }
            }
            echo "Done $command";
            break;

        case 'delReplace':
            if (isset($_GET['id'])) {
                $id = $_GET['id'];
                $fileToDelete = "$id.jpg";
                $logFilePath = 'uploads/upload_log.json';
                $logData = json_decode(file_get_contents($logFilePath), true);
                foreach ($logData as $key => $entry) {
                    if ($entry['file'] === $fileToDelete) {
                        unlink("/var/www/html/admin/uploads/" . $entry['file']);
                        unset($logData[$key]);
                        file_put_contents($logFilePath, json_encode(array_values($logData)));
                    }
                }
                $dataStream = getFileJsonData($STREAM);
                $dataStream['stream']['live'] = "true";
                $dataStream['stream']['id'] =  $id === 'default' ? '' : $_GET['prev'];
                saveJsonData($dataStream, $STREAM);
            }
            break;

        case 'delBg':
            if (isset($_GET['id'])) {
                $id = $_GET['id'];
                $fileToDelete = "$id.jpg";
                $logFilePath = 'uploads/upload_log.json';
                $logData = json_decode(file_get_contents($logFilePath), true);
                foreach ($logData as $key => $entry) {
                    if ($entry['file'] === $fileToDelete) {
                        unlink("/var/www/html/admin/uploads/" . $entry['file']);
                        unset($logData[$key]);
                        file_put_contents($logFilePath, json_encode(array_values($logData)));
                    }
                }
                $dataStream = getFileJsonData($STREAM);
                $dataStream['stream']['live'] = "true";
                //if (! file_exists("/var/www/html/".$dataStream['stream']['src']) ) {
                $dataStream['stream']['src'] = $id === 'default' ? '' : "$id.jpg";
                //}

                saveJsonData($dataStream, $STREAM);
                var_dump($dataStream);
                if (count($remotes) > 0) {
                    scpUploads();
                }
                echo "File deleted";
            } else {
                echo "Missing id parameter";
            }
            $_SESSION['GUI']['Tab'] == "System";
            break;

        case 'setBg':
            if (isset($_GET['status'])) {
                $live = $_GET['status'];
                $id = $_GET['id'];
                $dataStream = getFileJsonData($STREAM);
                $dataStream['stream']['live'] = $live;
                $dataStream['stream']['id'] = $id;
                $dataStream['stream']['src'] = $id === 'default' ? '' : "$id.jpg";
                saveJsonData($dataStream, $STREAM);
                if (count($remotes) > 0) {
                   scpUploads();
                }
                echo "Bg changed";
            } else {
                echo "Missing id parameter";
            }
            $_SESSION['GUI']['Tab'] == "System";
            break;

        case 'validatePict':
            if (isset($_GET['status'])) {
                $live = $_GET['status'];
                $dataStream = getFileJsonData($STREAM);
                $dataStream['stream']['live'] = $live;
                $dataStream['stream']['id'] = $_GET['id'];
                $dataStream['stream']['src'] = $_GET['id'] . ".jpg";
                saveJsonData($dataStream, $STREAM);
                if (count($remotes) > 0) {
                    scpUploads();
                }
                echo "Pict validated";
            } else {
                echo "Missing id parameter";
            }
            break;

        case 'changeDjName':
            if (isset($_GET['djName'])) {
                $formattedContent = str_replace("<br />", "\n", nl2br(htmlspecialchars(str_replace("[NEWLINE]", "\n", urldecode($_GET['djName'])))));
                setStreamValue('dj', $formattedContent, $STREAM);
                if (count($remotes) > 0) {
                    scpUploads();
                }
                echo "Dj name changed";
            } else {
                echo "Missing name parameter";
            }
            break;

        case 'restart':
            if (isset($_GET['service']) && isset($_GET['isLocal']) && isset($_GET['ip'])) {

                $command = "sudo systemctl restart " . escapeshellcmd($_GET['service']);
                if ($_GET['isLocal'] === 'true') {
                    $output = [];
                    $return_var = 0;
                    exec($command, $output, $return_var);
                    echo "Done $command";
                    break;
                }
                if (filter_var($_GET['ip'], FILTER_VALIDATE_IP)) {
                    sshCmd($_GET['ip'] . " $command");
                    break;
                }
            } else {
                echo "Forbidden";
            }
            break;

        case 'reboot':
            if (isset($_GET['isLocal']) && isset($_GET['ip'])) {
                echo $_GET['isLocal'] . " " . $_GET['ip'];
                $command = "sudo systemctl reboot";
                if ($_GET['isLocal'] == 'true') {
                    $output = [];
                    $return_var = 0;
                    exec($command, $output, $return_var);
                    echo "Done" . $command;
                    break;
                } else {
                    if (filter_var($_GET['ip'], FILTER_VALIDATE_IP)) {
                        sshCmd($_GET['ip'] . " $command");
                        break;
                    }
                }
            } else {
                echo "Forbidden";
            }
            break;

        case 'rebootAll':
            global $servers;

            if (isset($_GET['cmd']) && $_GET['cmd'] == 'rebootAll') {
                $out = '';
                $command = "sudo systemctl reboot";
                foreach ($servers as $key => $server) {
                    if (getWlan0Ip() === $server['ip']) {
                        $last = $server['ip'];
                    } else {
                        if (filter_var($server['ip'], FILTER_VALIDATE_IP)) {
                            sshCmd($server['ip'] . " $command");
                            break;
                        }
                    }
                }
                $output = [];
                $return_var = 0;
                exec($command, $output, $return_var);
                echo "Done" . $command;
            }
            break;
        default:
            echo "Unknown command";
            break;
    }
}
