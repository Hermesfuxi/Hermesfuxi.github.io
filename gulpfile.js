const gulp = require('gulp');
const cleanCSS = require('gulp-clean-css');
const purgecss = require('gulp-purgecss');
const htmlmin = require('gulp-htmlmin');
const uglify = require('gulp-uglify');
const replace = require('gulp-replace');
const inlineSource = require('gulp-inline-source');
const gzip = require('gulp-gzip'); // gzip压缩
const plumber = require('gulp-plumber'); // 错误处理

// 定义要去除的代码块，可以使用正则表达式
const patternsToRemove = {
    js: [/\/\*.*?\*\//gs, /console\.log.*?;/gs], // 移除所有注释和 console.log
    css: [/\/\*.*?\*\//gs], // 移除所有注释
    html: [/<!--.*?-->/gs] // 移除所有注释
};

// 处理 CSS 文件
gulp.task('minify-css', () => {
    return gulp.src('public/**/*.css')
        .pipe(plumber())
        .pipe(replace(patternsToRemove.css[0], '')) // 移除注释
        .pipe(cleanCSS({ compatibility: 'ie8' }))
        .pipe(purgecss({
            content: ['public/**/*.html']
        }))
        .pipe(gulp.dest('public'));
});

// 处理 JS 文件
gulp.task('minify-js', () => {
    return gulp.src('public/**/*.js')
        .pipe(plumber())
        .pipe(replace(patternsToRemove.js[0], '')) // 移除注释
        .pipe(replace(patternsToRemove.js[1], '')) // 移除 console.log
        .pipe(uglify())
        .pipe(gulp.dest('public'));
});

// 处理 HTML 文件
gulp.task('minify-html', () => {
    return gulp.src('public/**/*.html')
        .pipe(plumber())
        .pipe(replace(patternsToRemove.html[0], '')) // 移除注释
        .pipe(htmlmin({ collapseWhitespace: true, removeComments: true }))
        .pipe(inlineSource())
        .pipe(gulp.dest('public'));
});

// Gzip 压缩 HTML、JS 和 CSS 文件
gulp.task('gzip', () => {
    return gulp.src('public/**/*.{html,js,css}')
        .pipe(gzip())
        .pipe(gulp.dest('public'));
});

// 注册任务:定义默认任务
gulp.task('default', gulp.series('minify-css', 'minify-js', 'minify-html', 'gzip'));
