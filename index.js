const puppeteer = require('puppeteer');


(async() => {
    // VARS
    const LIVE = false

    // time we can book the competition today, if it's in the past we assume can book now
    const kick_off_time = "21:44:00:00"

    // date of competition in future
    const desired_date = '3 Dec'

    // unique word in the competition title to distinguish it from other comps on the same day
    const keyword = null

    // tee times we want in order of preference
    const time_slots = ['11:00', '11:10', '11:20', '11:30', '11:40', '11:50', '12:00', '12:10', '12:20', '12:30']

    // ID's for the <select> of the <option> values of the players we want to play with
    const player1 = 26 // Tony Brown
    const player2 = 101 // Rhys Griffith
    const player3 = 61 // Jeff Davies

    // not really the username, it's the value of the <option> to set the <select> to on the login page
    const username = "254:~:Smith, Anthony "
    const password = ""


    // setup chrome
    const browser = await puppeteer.launch()
    const page = await browser.newPage()
    page.on('console', msg => console.log(msg.text()));


    // Login
    await page.goto('https://www.masterscoreboard.co.uk/ClubIndex.php?CWID=5070', {
        waitUntil: 'networkidle0',
        timeout: 10000
    })

    await page.evaluate((username, password) => {
        document.querySelector('select').value = username
        document.querySelector('input[type="password"]').value = password
    }, username, password)

    await Promise.all([
        page.click('input[value="Log in"]'),
        page.waitForNavigation({
            waitUntil: 'networkidle0'
        })
    ])

    // logged in, now we can wait until the comp is live
    await page.waitForFunction((kick_off_time) => {
        // can't pass in date objects to here so do the parsing here, probably doesn't take long
        const kick_off = new Date()
        kick_off.setHours(parseInt(kick_off_time.split(':')[0]))
        kick_off.setMinutes(parseInt(kick_off_time.split(':')[1]))
        kick_off.setSeconds(parseInt(kick_off_time.split(':')[2]))

        const now = new Date()
        if (kick_off < now) {
            return true
        }
        console.log(`Waiting - ${kick_off - now} milliseconds left`)
    }, {
        polling: 100,
        timeout: 0
    }, kick_off_time)

    await page.evaluate(() => console.log('Time to go - ', new Date().toLocaleTimeString()))

    // go to competition page and find the comp we want
    await page.goto('https://www.masterscoreboard.co.uk/ListOfFutureCompetitions.php?CWID=5070', {
        waitUntil: 'networkidle0',
        timeout: 10000
    })

    const action = await page.evaluate((desired_date, keyword) => {
        // go through the rows and find the comp that we want to book
        const nodes = document.querySelectorAll('tr')
        const row = Array.from(nodes).find(node => {
            if (!node.innerText.includes(desired_date))
                return false
            if (keyword && !node.innerText.toLowerCase().includes(keyword)) {
                return false
            }
            return true
        })
        let form = null
        try {
            form = row.querySelector('form')
        } catch { // TODO make this a loop, refresh the page
            console.error("Competition is not available yet, try again")
        }
        return form.action
    }, desired_date, keyword)

    // load competition page
    await page.goto(action, {
        waitUntil: 'networkidle0',
        timeout: 10000
    })

    await page.screenshot({
        path: '5.Clicked into the competition and loaded.png'
    })

    const inpu = await page.evaluateHandle((time_slots) => {
        // loop through slots until we find an available one
        let input = null
        do {
            Array.from(document.querySelectorAll('tr')).forEach(node => {
                if (!!node.innerText.trim()) {
                    return
                }
                const inp = node.querySelector('input')
                const viable = time_slots.some(slot => {
                    if (inp.value.includes(slot)) {
                        console.log(`found slot: ${slot}`)
                        return true
                    }
                    return false
                })
                if (viable) {
                    console.log('viable')
                    input = inp
                }
            })
        }
        while (!input)
        console.log(input)
        return input
    }, time_slots)

    await inpu.click()

    await page.screenshot({
        path: '6.Filling in players.png'
    })

    await page.evaluate((player1, player2, player3) => {
        const [select1, select2, select3] = document.querySelectorAll('select')
        select1.value = player1
        select2.value = player2
        select3.value = player3
    }, player1, player2, player3)

    if (!LIVE) {
        await browser.close()
    }
    // WARNING past this point we're actually booking


})();