<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Doughnut Chart</title>
    <style>
        .chart-container {
            display: flex;
            align-items: center;
        }
        #doughnutChart {
            width: 100px; /* Fixed width for the canvas */
            height: 100px; /* Fixed height for the canvas */
        }
        .text-info {
            margin-left: 15px; /* Space between chart and text */
            font-family: Arial, sans-serif;
            font-size: 12px;
            line-height: 1.5;
        }
        .text-info p {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <h1>Storage Usage</h1>
    <div class="chart-container">
        <canvas id="doughnutChart" width="100" height="100"></canvas>
        <div class="text-info">
            <p><strong>Folder Usage:</strong> 
                <?php 
                    echo ($folderSize < (1024 * 1024 * 1024)) 
                        ? round($folderSize / (1024 * 1024), 2) . " Mo" 
                        : round($folderSize / (1024 * 1024 * 1024), 2) . " Go"; 
                ?>
            </p>
            <p><strong>Allocated Space:</strong> 
                <?php 
                    echo ($allocatedSpace < (1024 * 1024 * 1024)) 
                        ? round($allocatedSpace / (1024 * 1024), 2) . " Mo" 
                        : round($allocatedSpace / (1024 * 1024 * 1024), 2) . " Go"; 
                ?>
            </p>
            <p><strong>Remaining Space:</strong> 
                <?php 
                    $remainingSpace = $diskTotalSize - $folderSize - $allocatedSpace;
                    echo ($remainingSpace < (1024 * 1024 * 1024)) 
                        ? round($remainingSpace / (1024 * 1024), 2) . " Mo" 
                        : round($remainingSpace / (1024 * 1024 * 1024), 2) . " Go"; 
                ?>
            </p>
        </div>
    </div>

    <script>
        // Storage data (replace these values dynamically with PHP)
        const totalSpace = <?php echo $diskTotalSize; ?>; // Total storage in bytes
        const allocatedSpace = <?php echo $allocatedSpace; ?>; // Allocated storage in bytes
        const folderSize = <?php echo $folderSize; ?>; // Folder size in bytes
        const remainingSpace = totalSpace - folderSize - allocatedSpace;

        // Data for the chart
        const data = [
            folderSize,         // Grey - Folder Usage
            allocatedSpace,     // Orange - Allocated Space
            remainingSpace,     // Blue - Remaining Space
        ];
        const colors = ['grey', 'orange', 'blue'];

        // Draw the Doughnut Chart
        const canvas = document.getElementById('doughnutChart');
        const ctx = canvas.getContext('2d');

        // Clear the canvas before drawing
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Center and radius for the chart
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 45; // Adjusted for 100x100 canvas
        const cutoutRadius = 20; // Inner circle for Doughnut effect
        const totalValue = data.reduce((acc, val) => acc + val, 0);

        let startAngle = 0;

        data.forEach((value, index) => {
            const sliceAngle = (value / totalValue) * 2 * Math.PI;

            // Draw outer arc
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
            ctx.arc(centerX, centerY, cutoutRadius, startAngle + sliceAngle, startAngle, true);
            ctx.closePath();

            ctx.fillStyle = colors[index];
            ctx.fill();

            // Update start angle for next slice
            startAngle += sliceAngle;
        });
    </script>
</body>
</html>
