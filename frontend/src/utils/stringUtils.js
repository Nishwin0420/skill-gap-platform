/**
 * Utility functions for string manipulation and formatting.
 */

/**
 * Converts a skill string to Title Case.
 * Example: "machine learning" -> "Machine Learning"
 * Example: "aws" -> "AWS"
 * 
 * @param {string} str - The string to convert.
 * @returns {string} The Title Cased string.
 */
export const toTitleCase = (str) => {
  if (!str) return '';
  
  // Special cases for common acronyms/tech terms that should be fully capitalized
  const acronyms = new Set(['aws', 'gcp', 'api', 'ui', 'ux', 'ai', 'ml', 'nlp', 'sql', 'css', 'html', 'ci', 'cd', 'ci/cd', 'llm']);
  
  return str.split(' ').map(word => {
    const lowerWord = word.toLowerCase();
    if (acronyms.has(lowerWord)) {
      return word.toUpperCase();
    }
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
  }).join(' ');
};
