module.exports = {
  env: {
    es6: true,
    node: true,
    jest: true,
  },
  extends: ['airbnb-base', 'prettier', 'plugin:jest/recommended'],
  plugins: ['jest'],
  globals: {
    Atomics: 'readonly',
    SharedArrayBuffer: 'readonly',
    API_BASE: 'writable',
    HUMAN_GEM_VERSION: 'writable',
  },
  parserOptions: {
    ecmaVersion: 2018,
    sourceType: 'module',
  },
  rules: {
    'no-plusplus': 'off',
    'no-unused-vars': 'off',
    'prefer-const': 'off',
    'no-restricted-syntax': 'off',
    'block-scoped-var': 'off',
    camelcase: 'off',
    'consistent-return': 'off',
    eqeqeq: 'off',
    'import/newline-after-import': 'off',
    'import/no-unresolved': 'off',
    'no-console': 'off',
    'no-extra-boolean-cast': 'off',
    'no-param-reassign': 'off',
    'no-return-await': 'off',
    'no-shadow': 'off',
    'no-use-before-define': 'off',
    'no-useless-escape': 'off',
    'no-var': 'off',
    'one-var': 'off',
    radix: 'off',
    'vars-on-top': 'off',
    'no-underscore-dangle': 'off',
    'dot-notation': 'off',
    'import/prefer-default-export': 'off',
    'global-require': 'off',
    'prefer-arrow-callback': 'off',
    'func-names': 'off',
  },
};
