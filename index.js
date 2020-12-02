const puppeteer = require('puppeteer');


(async() => {
    // VARS

    const now = new Date()
    if (now.getDay() !== 3) { // only run on fridays
        console.error("Only run on fridays")
        await browser.close();
        return
    }
    // time we can book the competition today, if it's in the past we assume can book now
    // const kick_off_time = "20:00:00:00"
    const kick_off_time = "09:00:00:00"


    const ko = new Date()
    ko.setHours(parseInt(kick_off_time.split(':')[0]))
    ko.setMinutes(parseInt(kick_off_time.split(':')[1]))
    ko.setSeconds(parseInt(kick_off_time.split(':')[2]))

    if (ko - now > (1000 * 60 * 10)) { // kick off is more than 10 mins ahead so in the future
        console.error("Too early")
        await browser.close()
        return
    }
    if (ko - now < 0) { // kick off is in the past
        console.error("Done for the day")
        await browser.close()
        return
    }


    // date of competition in future
    const desired_date = '5 Dec'

    // unique word in the competition title to distinguish it from other comps on the same day
    const keyword = 'stableford'

    // tee times we want in order of preference
    const time_slots = [
        '11:00', '11:10', '11:20', '11:30', '11:40', '11:50',
        '12:00', '12:10', '12:20', '12:30', '12:40', '12:50',
        '13:00', '13:10', '13:20', '13:30', '13:40', '13:50',
    ]

    // ID's for the <select> of the <option> values of the players we want to play with
    const player1 = 26 // Tony Brown
    const player2 = 101 // Rhys Griffith
    const player3 = 61 // Jeff Davies

    // not really the username, it's the value of the <option> to set the <select> to on the login page
    const username = "254:~:Smith, Anthony "
    const password = process.env.MS_PASS


    // setup chrome
    const browser = await puppeteer.launch({
        args: ['--no-sandbox']
    })
    const page = await browser.newPage()
    page.on('console', msg => console.log(msg.text()));


    // Login
    await page.goto('https://www.masterscoreboard.co.uk/ClubIndex.php?CWID=5070', {
        waitUntil: 'networkidle0',
        timeout: 1000
    })

    await page.evaluate((username, password) => {
        document.querySelector('select').value = username
        document.querySelector('input[type="password"]').value = password
    }, username, password)

    await Promise.all([
        page.click('input[value="Log in"]'),
        page.waitForNavigation({
            waitUntil: 'networkidle0',
            timeout: 1000
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

    async function load_comp(desired_date, keyword) {
        // go to competition page and find the comp we want
        await page.goto('https://www.masterscoreboard.co.uk/ListOfFutureCompetitions.php?CWID=5070', {
            waitUntil: 'networkidle0',
            timeout: 1000
        })

        const action = await page.evaluate((desired_date, keyword) => {
            // go through the rows and find the comp that we want to book
            const nodes = document.querySelectorAll('tr')
            const row = Array.from(nodes).find(node => {
                if (!node.innerText.toLowerCase().includes(desired_date.toLowerCase()))
                    return false
                if (keyword && !node.innerText.toLowerCase().includes(keyword.toLowerCase())) {
                    return false
                }
                return true
            })
            if (!row) {
                console.error(`Row not found, for desired_date: '${desired_date}' or keyword: '${keyword}'`)
                return null
            }
            let form = row.querySelector('form')
            if (!form) {
                console.error("Could not get form of row")
                return null
            }
            return form.action
        }, desired_date, keyword)
        return action
    }

    const action = await load_comp(desired_date, keyword)

    if (!action) {
        console.error("Could not get form of page")
        await browser.close()
        return
    }
    // load competition page
    await page.goto(action, {
        waitUntil: 'networkidle0',
        timeout: 1000
    })

    const input_selector = await page.evaluate(time_slots => {
        for (const slot of time_slots) {
            // TODO handle In Use slots
            let str = `input[value="${slot}     Book"`
            const inp = document.querySelector(str)
            if (!inp) {
                console.log(`slot: ${slot} unviable - full or not available`)
                continue
            }
            const tr = inp.closest('tr')
            if (!!tr.innerText.trim()) {
                console.log(`slot: ${slot} unviable - other players`)
                continue
            }
            console.log(`going with: ${slot}`)
            return str
        }
    }, time_slots)

    if (!input_selector) {
        console.error("Could not find any suitable time slot on page")
        await browser.close()
        return
    }

    await page.$eval(input_selector, e => {
        e.scrollIntoView()
        e.click()
    }, input_selector)

    await page.evaluate((player1, player2, player3) => {
        const [select1, select2, select3] = document.querySelectorAll('select')
        select1.value = player1
        select2.value = player2
        select3.value = player3
    }, player1, player2, player3)


    await page.$eval('input[type="submit"]', e => e.click())
    await page.evaluate(() => console.log('booked'))

    await browser.close()
})();