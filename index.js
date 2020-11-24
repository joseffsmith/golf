// https://www.masterscoreboard.co.uk/
// CWID = 5070
// MSBid = 75d4be0a17ff8f1dfb85c1b161224589

/*
 *  With a CWID of 5070 as a url param and MSBid
 *  Generating an MSBid will need to be done so that the cookie is set
 */

// on https://www.masterscoreboard.co.uk/ListOfFutureCompetitions.php
// date must be '5 Jan' or '16 Dec'
let date = '1 Dec'

let row = null
document.querySelectorAll('tr').forEach(node => {
    if (!node.innerText.includes(date))
        return
    if (node.innerText.toLowerCase().includes('ladies')) {
        return
    }
    row = node
})
url = row.querySelector('form').action
window.location = url

// probably need to pause here
// expect to now be on bookings1/Book.php?CWID=5070&intCompID=151151
// note we still have CWID but MSBid is
let time_slots = ['12:00', '12:10', '12:20', '12:30']


let done = false
time_slots.forEach(slot => {
    if (done === true) {
        return
    }
    const value = `${slot}     Book`
    try {
        document.querySelector(`input[value="${value}"]`).click()
        done = true
    } catch {
        console.warn(`Couldn't get slot: ${slot}`)
    }
})

// probably need to pause here
// expect to now be on bookings1/BookSelectPartners.php?CWID=5070

// option value = "27" > Brown, Antony < /option> <
// option value = "101" > Griffith, Rhys < /option> <
// option value = "61" > Davies, Jeff < /option>
const [player1, player2, player3] = document.querySelectorAll('select')
player1.value = 27
player2.value = 101
player3.value = 61