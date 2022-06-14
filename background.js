browser.tabs.onUpdated.addListener(function (tabId, changeInfo) {
  if (changeInfo.status == 'complete') {
    findGameType()
  }
})

// Finds out whether the game is blitz/bullet/rapid or classical
const findGameType = () => {
  console.log('GAMETYPE')
}
