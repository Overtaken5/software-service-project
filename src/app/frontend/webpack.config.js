const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './src/index.js', 
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
    clean: true, 
  },
  mode: 'development', 
  devServer: {
    static: './dist',
    port: 3000, 
    open: true, 
  },
  module: {
    rules: [

      {
        test: /\.scss$/,
        use: ['style-loader', 'css-loader', 'sass-loader'],
      },

      {
        test: /\.html$/,
        use: ['html-loader'],
      },

      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
          },
        },
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './src/index.html',
    }),
  ],
};
