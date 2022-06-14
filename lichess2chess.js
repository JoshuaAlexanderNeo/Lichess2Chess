const GAME_TYPES = {
  BLITZ: 'Blitz',
  BULLET: 'Bullet',
  RAPID: 'Rapid',
  CLASSICAL: 'Classical',
  CORRESPONDENCE: 'Correspondence',
  UNKNOWN: 'Unknown'
}

// Finds out whether the game is blitz/bullet/rapid or classical
const findGameType = () => {
  const gameType = document.querySelector('.setup').lastChild
  if (gameType?.title && gameType.outerText.includes(GAME_TYPES.CORRESPONDENCE)) {
    return GAME_TYPES.CORRESPONDENCE
  } else if (gameType?.title && gameType.outerText.includes(GAME_TYPES.BLITZ)) {
    return GAME_TYPES.BLITZ
  } else if (gameType?.title && gameType.outerText.includes(GAME_TYPES.BULLET)) {
    return GAME_TYPES.BULLET
  } else if (gameType?.title && gameType.outerText.includes(GAME_TYPES.RAPID)) {
    return GAME_TYPES.RAPID
  } else if (gameType?.title && gameType.outerText.includes(GAME_TYPES.CLASSICAL)) {
    return GAME_TYPES.CLASSICAL
  } else {
    return GAME_TYPES.UNKNOWN
  }
}

// Finds all <rating> elements on the page
const getAllLichessRatings = () => {
  const rating = document.querySelectorAll('.ruser > rating')
  return rating
}

// lineear regression
const calculateRegression = (regression, lichessRating) => {
  return Math.round((lichessRating - regression[1]) / regression[0])
}

// Adds the chess.com rating equivalent beside the lichess rating.
const addChessComRating = (gameType, lichessRatings) => {
  // all regressions calculated from chessgoals.com on 15/06/2022
  const BLITZ_REGRESSION = [0.77735, 581.148]
  const BULLET_REGRESSION = [0.819536, 430.42]
  const RAPID_REGRESSION = [0.618176, 943.688]
  const CLASSICAL_REGRESSION = [0.500363, 1086.75]

  let regression

  if (gameType === GAME_TYPES.BLITZ) {
    regression = BLITZ_REGRESSION
  } else if (gameType === GAME_TYPES.BULLET) {
    regression = BULLET_REGRESSION
  } else if (gameType === GAME_TYPES.RAPID) {
    regression = RAPID_REGRESSION
  } else {
    regression = CLASSICAL_REGRESSION
  }

  for (rating of lichessRatings) {
    const lichessRating = parseInt(rating.innerText)
    const chessComRating = calculateRegression(regression, lichessRating)
    let chessComRatingDiv = document.createElement('div')
    chessComRatingDiv.style.setProperty('color', '#769656')
    chessComRatingDiv.innerText = `(${chessComRating})`
    rating.parentNode.appendChild(chessComRatingDiv)
    rating.parentNode.insertBefore(chessComRatingDiv, rating.nextSibling)
  }

  return lichessRatings
}

const gameType = findGameType()
if (gameType === GAME_TYPES.UNKNOWN) {
  console.log('Game type not found')
} else {
  const lichessRatings = getAllLichessRatings()
  addChessComRating(gameType, lichessRatings)
}
