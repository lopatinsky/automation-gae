var gulp = require('gulp'),
    reactify = require('reactify'),
    browserify = require('browserify'),
    concat = require('gulp-concat'),
    uglify = require('gulp-uglify'),
    babelify = require('babelify'),
    watchify = require('watchify'),
    source = require('vinyl-source-stream'),
    buffer = require('vinyl-buffer'),
    sourcemaps = require('gulp-sourcemaps');

var path = {
    STYLES: ['static/demo/src/styles/*.*'],
    STYLES_OUT: 'static/demo/dist/styles',
    FONTS: 'node_modules/bootstrap/fonts/*.*',
    FONTS_OUT: 'static/demo/dist/fonts',
    SCRIPT_MAIN: 'static/demo/src/scripts/main',
    SCRIPTS_OUT: 'static/demo/dist/scripts'
};

gulp.task('styles', function() {
    gulp.src(path.STYLES)
        .pipe(concat('bundle.css'))
        .pipe(gulp.dest(path.STYLES_OUT));
    gulp.src(path.FONTS)
        .pipe(gulp.dest(path.FONTS_OUT));
});

function _build(x) {
    return x
        .bundle()
        .on('error', function(e) { console.log(e) })
        .pipe(source('bundle.js'))
        .pipe(buffer())
        .pipe(sourcemaps.init({loadMaps: true}))
        .pipe(uglify('bundle.js'))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(path.SCRIPTS_OUT));
}

gulp.task('scripts', function() {
    _build(browserify({
        entries: path.SCRIPT_MAIN,
        transform: [babelify, reactify],
        extensions: ['.jsx'],
        debug: true
    }));
});

gulp.task('default', ['scripts', 'styles']);

gulp.task('watch', ['styles'], function () {
    gulp.watch(path.STYLES, ['styles']);
    gulp.watch(path.FONTS, ['styles']);

    var watcher = watchify(browserify({
        entries: path.SCRIPT_MAIN,
        transform: [babelify, reactify],
        extensions: ['.jsx'],
        debug: true,
        cache: {}, packageCache: {}, fullPaths: true
    }));
    return _build(watcher.on('update', function() {
        _build(watcher);
    }));
});
