export const WORDLE_COLORS = {
  green: 'bg-wordle-green',
  yellow: 'bg-wordle-yellow',
  gray: 'bg-wordle-gray',
} as const

export const DEFAULT_WORD_LENGTH = 5
export const DEFAULT_MAX_GUESSES = 6
export const DEFAULT_WORD_BANK = 'CET4'

export const KEYBOARD_ROWS = [
  ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
  ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
  ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'BACKSPACE'],
]