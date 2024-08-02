const gulp = require('gulp');
const cleanCSS = require('gulp-clean-css');
const purgecss = require('gulp-purgecss');
const htmlmin = require('gulp-htmlmin');
const uglify = require('gulp-uglify');
const inlineSource = require('gulp-inline-source');
const gzip = require('gulp-gzip');
const plumber = require('gulp-plumber');
const brotli = require('gulp-brotli');
// const rename = require('gulp-rename');


// 处理 CSS 文件
gulp.task('minify-css', () => {
    return gulp.src('public/**/*.css')
        .pipe(plumber())
        // .pipe(postcss([autoprefixer()])) // 使用 postcss 和 autoprefixer 处理 CSS
        .pipe(cleanCSS({ compatibility: 'ie8' })) // 使用更现代的插件并移除注释
        // .pipe(purgecss({
        //     content: ['public/**/*.html']
        // }))
        // .pipe(rename({ suffix: '.min' }))
        .pipe(gulp.dest('public'));
});


// 处理 JS 文件
gulp.task('minify-js', () => {
    return gulp.src('public/**/*.js')
        .pipe(plumber())
        .pipe(uglify()) // 会移除注释和 console.log
        // .pipe(rename({ suffix: '.min' }))
        .pipe(gulp.dest('public'));
});

// 处理 HTML 文件
gulp.task('minify-html', () => {
    return gulp.src('public/**/*.html')
        .pipe(plumber())
        .pipe(htmlmin({
            minifyJS: true,
            minifyCSS: true,
            minifyURLs: true,
            collapseWhitespace: true,
            removeComments: true // 移除所有注释
        }))
        .pipe(inlineSource()) // 将外部资源内联
        // .pipe(rename({ suffix: '.min' }))
        .pipe(gulp.dest('public'));
});

// Gzip 压缩 HTML、JS 和 CSS 文件
gulp.task('gzip', () => {
    return gulp.src('public/**/*.{html,js,css}')
        .pipe(gzip())
        .pipe(gulp.dest('public'));
});

// Brotli 压缩 JS、CSS 和 HTML 文件
gulp.task('brotli', () => {
    return gulp.src(['public/**/*.js', 'public/**/*.css', 'public/**/*.html'])
        .pipe(brotli({
            extension: 'br',
            quality: 11,
            mode: 'text',
            keepUncompressed: true
        }))
        .pipe(gulp.dest('public'));
});

// 注册任务:定义默认任务
gulp.task('default', gulp.series('minify-css', 'minify-js', 'minify-html', 'gzip', 'brotli'));