export function toDatetimeInputString(date: Date) {
    let datetime = new Date()
    datetime.setTime(date.getTime() - date.getTimezoneOffset() * 60 * 1000)
    let dateString = datetime.toISOString().split(':').slice(0, 2).join(':')
    return dateString
}