
function update_streamer(data) {

    $('#streamer-status').text(data.running ? 'Collecting..' : 'Stopped');
    $('#streamer-rules').empty()
    for(let rule of data.rules) {
        console.log(rule)
        $('#streamer-rules').append(`<tr><td>${rule.id}</td><td>${rule.name}</td><td>${rule.tag}</td><td>${rule.query}</td><td>${rule.api_id}</td></tr>`);
    }

    $('#streamer-run').val(data.running ? 'Stop' : 'Start')
}

function update_all_rules(data) {
    $('#all-rules').empty()
    data.rules.sort((a,b) => b.tweet_count - a.tweet_count)

    for(let rule of data.rules) {
        $('#all-rules').append(`<tr><td>${rule.id}</td><td>${rule.type}</td><td>${rule.name}</td><td>${rule.tag}</td><td>${rule.tweet_count}</td><td>${rule.query}</td></tr>`);
    }
}

function update_downloader(data) {
    $('#downloader-status').text(data.running ? 'Ready' : 'Stopped');
    $('#downloader-queue-size').text(data.queue_size)
    $('#downloader-root-dir').text(data.root_dir)
    $('#downloader-downloading').text(data.downloading.url)
    $('#downloader-start-stop').val(data.running ? 'Deactivate' : 'Activate')
}

function fetch_streamer_update() {
    $.getJSON('/streamer', function(data) {
        console.log(data)
        update_streamer(data)
    })
}

function fetch_downloader_update() {
    $.getJSON('/downloader', function(data) {
        console.log(data)
        update_downloader(data)
    })
}

function fetch_all_rules_update() {
    $.getJSON('/rules', function(data) {
        console.log(data)
        update_all_rules(data)
    })
}

function initial_load() {
    fetch_streamer_update()
    fetch_downloader_update()
    fetch_all_rules_update()
}

initial_load()

// var update_task = setInterval(fetch_downloader_update, 2000);