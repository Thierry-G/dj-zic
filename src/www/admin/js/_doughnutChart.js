export function drawChart() {
    const canvas = document.getElementById('doughnutChart');
    const ctx = canvas.getContext('2d');

    // Get the elements & convert data attributes to numbers
    const total = document.getElementById('chart');
    const totalSpace = Number(total.dataset.size);

    const folder = document.getElementById('folderSize');
    const folderSize = Number(folder.dataset.size);  // Corrected

    const allocatedSpace = document.getElementById('allocatedSpace');
    const allocatedSpaceValue = Number(allocatedSpace.dataset.size);  // Corrected

    const remainingSpace = totalSpace - folderSize - allocatedSpaceValue;

    const colors = ['grey', 'orange', 'blue'];
    const data = [folderSize, allocatedSpaceValue, remainingSpace];

    // Draw the Doughnut Chart
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 45;
    const cutoutRadius = 20;
    const totalValue = data.reduce((acc, val) => acc + val, 0);

    let startAngle = 0;

    data.forEach((value, index) => {
        const sliceAngle = (value / totalValue) * 2 * Math.PI;

        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
        ctx.arc(centerX, centerY, cutoutRadius, startAngle + sliceAngle, startAngle, true);
        ctx.closePath();

        ctx.fillStyle = colors[index];
        ctx.fill();

        startAngle += sliceAngle;
    });
}
