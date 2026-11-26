import nextCoreWebVitals from 'eslint-config-next/core-web-vitals';

/** @type {import('eslint').Linter.Config[]} */
const eslintConfig = [
  ...nextCoreWebVitals,
  {
    rules: {
      // React Compiler rules added in react-hooks v7 (shipped with Next 16).
      // Existing components predate them; surface as warnings until refactored.
      'react-hooks/set-state-in-effect': 'warn',
      'react-hooks/purity': 'warn',
      'react-hooks/immutability': 'warn',
    },
  },
  {
    ignores: [
      'app/**/*.bak',
      'app/**/*.backup.tsx',
      'app/**/*.before-*.tsx',
    ],
  },
];

export default eslintConfig;
