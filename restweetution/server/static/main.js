
function update_streamer(data) {

    $('#streamer-status').text(data.running ? 'Collecting..' : 'Stopped');

    for(let rule of data.rules) {
        console.log(rule)
        $('#streamer-rules tr:last').after(`<tr><td>${rule.id}</td><td>${rule.name}</td><td>${rule.tag}</td><td>${rule.query}</td><td>${rule.api_id}</td></tr>`);
    }

    $('#streamer-run').val(data.running ? 'Stop' : 'Start')
}

function update_downloader(data) {
    $('#downloader-status').text(data.running ? 'Ready' : 'Stopped');
    $('#downloader-queue-size').text(data.queue_size)
    $('#downloader-root-dir').text(data.root_dir)
    $('#downloader-downloading').text(data.downloading.url)
    $('#downloader-start-stop').val(data.running ? 'Deactivate' : 'Activate')
}

$.getJSON('/streamer', function(data) {
    console.log(data)
    update_streamer(data)
})

function fetch_downloader_update() {
    $.getJSON('/downloader', function(data) {
        console.log(data)
        update_downloader(data)
    })
}

fetch_downloader_update()

// var update_task = setInterval(fetch_downloader_update, 2000);