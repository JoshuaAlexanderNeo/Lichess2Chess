const GAME_TYPES = {
  BLITZ: 'Blitz',
  BULLET: 'Bullet',
  RAPID: 'Rapid',
  CLASSICAL: 'Classical',
  CORRESPONDENCE: 'Correspondence',
  UNKNOWN: 'Unknown'
}

// all regressions calculated from chessgoals.com on 15/06/2022
const BLITZ_REGRESSION = [0.000169095, 0.665195, -214.973]
const BULLET_REGRESSION = [-6.0463e-8, 0.000302882, 0.787848, -418.114]
const RAPID_REGRESSION = [1.25804, -795.231]
const CLASSICAL_REGRESSION = [0.00033735, 0.267304, -79.3846]

// Finds out whether the game is blitz/bullet/rapid or classical
const findGameType = () => {
  let type = document.querySelector('.setup')

  if (type !== null) {
    type = type.lastChild
  } else {
    return GAME_TYPES.UNKNOWN
  }
  if (type?.title && type.outerText.includes(GAME_TYPES.CORRESPONDENCE)) {
    return GAME_TYPES.CORRESPONDENCE
  } else if (type?.title && type.outerText.includes(GAME_TYPES.BLITZ)) {
    return GAME_TYPES.BLITZ
  } else if (type?.title && type.outerText.includes(GAME_TYPES.BULLET)) {
    return GAME_TYPES.BULLET
  } else if (type?.title && type.outerText.includes(GAME_TYPES.RAPID)) {
    return GAME_TYPES.RAPID
  } else if (type?.title && type.outerText.includes(GAME_TYPES.CLASSICAL)) {
    return GAME_TYPES.CLASSICAL
  } else {
    return GAME_TYPES.UNKNOWN
  }
}

// Finds all both ratings in a game
const getLichessRatingsFromGame = () => {
  const rating = document.querySelectorAll('.ruser > rating')
  return rating
}

const getLichessRatingsFromProfile = () => {
  const ratings = document.querySelectorAll('.sub-ratings rating')
  return ratings
}

// Calculates the chess.com rating based on the regression
const calculateRegression = (regression, lichessRating) => {
  if (regression.length === 2) {
    return Math.round(regression[0] * lichessRating + regression[1])
  } else if (regression.length === 3) {
    return Math.round(regression[0] * (lichessRating * lichessRating) + regression[1] * lichessRating + regression[2])
  } else {
    return Math.round(
      regression[0] * (lichessRating * lichessRating * lichessRating) +
        regression[1] * (lichessRating * lichessRating) +
        regression[2] * lichessRating +
        regression[3]
    )
  }
}

// Adds ratings to the left-most sidebar.
const addChessComRatingToProfile = (lichessRatings) => {
  for (rating of lichessRatings) {
    console.log(rating)
    let regression
    if (rating.previousElementSibling.innerHTML === GAME_TYPES.BULLET) {
      regression = BULLET_REGRESSION
    } else if (rating.previousElementSibling.innerHTML === GAME_TYPES.BLITZ) {
      regression = BLITZ_REGRESSION
    } else if (rating.previousElementSibling.innerHTML === GAME_TYPES.RAPID) {
      regression = RAPID_REGRESSION
    } else if (rating.previousElementSibling.innerHTML === GAME_TYPES.CLASSICAL) {
      regression = CLASSICAL_REGRESSION
    }

    if (regression && rating.innerText[0] !== '?') {
      const lichessRating = parseInt(rating.textContent)
      const chessComRating = calculateRegression(regression, lichessRating)
      let chessComRatingDiv = document.createElement('div')
      chessComRatingDiv.style.setProperty('color', '#769656')
      chessComRatingDiv.innerText = `(${chessComRating})`
      rating.firstChild.appendChild(chessComRatingDiv)
    }
  }
}

// Adds the chess.com rating equivalent beside the lichess rating.
const addChessComRatingToGame = (gameType, lichessRatings) => {
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
  // check if on a profile
  const profileRatings = getLichessRatingsFromProfile()
  addChessComRatingToProfile(profileRatings)
} else {
  // in a game, add the chess.com rating to the game
  const lichessRatings = getLichessRatingsFromGame()
  addChessComRatingToGame(gameType, lichessRatings)
}
