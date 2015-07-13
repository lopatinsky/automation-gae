var gulp = require('gulp'),
    reactify = require('reactify'),
    browserify = require('browserify'),
    concat = require('gulp-concat'),
    uglify = require('gulp-uglify'),
    babelify = require('babelify'),
    watchify = require('watchify'),
    buffer = require('vinyl-buffer'),
    sourcemaps = require('gulp-sourcemaps');

gulp.task('styles', function() {
    gulp.src(['node_modules/bootswatch/simplex/bootstrap.min.css'])
        .pipe(gulp.dest('static/demo/dist/styles'));
    gulp.src(['node_modules/bootstrap/fonts/*.*'])
        .pipe(gulp.dest('static/demo/dist/fonts'));
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
        .pipe(gulp.dest('static/demo/dist/scripts'));
}

gulp.task('scripts', function() {
    _build(browserify({
        entries: ['static/demo/src/scripts/main'],
        transform: [babelify, reactify],
        extensions: ['.jsx'],
        debug: true
    }));
});

gulp.task('default', ['scripts', 'styles']);

gulp.task('watch', function () {
    var watcher = watchify(browserify({
        entries: ['static/demo/src/scripts/main'],
        transform: [babelify, reactify],
        extensions: ['.jsx'],
        debug: true,
        cache: {}, packageCache: {}, fullPaths: true
    }));
    return _build(watcher.on('update', function() {
        _build(watcher);
    }));
});
