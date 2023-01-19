export function toDatetimeInputString(date: Date) {
    let datetime = new Date()
    datetime.setTime(date.getTime() - date.getTimezoneOffset() * 60 * 1000)
    let dateString = datetime.toISOString().split(':').slice(0, 2).join(':')
    return dateString
}


/** assumes array elements are primitive types
* check whether 2 arrays are equal sets.
* @param  {} a1 is an array
* @param  {} a2 is an array
*/
export function areArraysEqualSets(a1: any[], a2: any[]) {
    const superSet: any = {};
    for (const i of a1) {
      const e = i + typeof i;
      superSet[e] = 1;
    }
  
    for (const i of a2) {
      const e = i + typeof i;
      if (!superSet[e]) {
        return false;
      }
      superSet[e] = 2;
    }
  
    for (let e in superSet) {
      if (superSet[e] === 1) {
        return false;
      }
    }
  
    return true;
  }