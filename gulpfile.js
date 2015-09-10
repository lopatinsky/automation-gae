var gulp = require('gulp'),
    gutil = require('gulp-util'),
    reactify = require('reactify'),
    browserify = require('browserify'),
    concat = require('gulp-concat'),
    uglify = require('gulp-uglify'),
    babelify = require('babelify'),
    watchify = require('watchify'),
    source = require('vinyl-source-stream'),
    buffer = require('vinyl-buffer'),
    sourcemaps = require('gulp-sourcemaps');

var targets = {
    wizard: {
        STYLES: ['node_modules/react-spinner/react-spinner.css', 'frontend-src/demo/styles/*.*'],
        STYLES_OUT: 'static/demo/styles',
        FONTS: 'node_modules/bootstrap/fonts/*.*',
        FONTS_OUT: 'static/demo/fonts',
        SCRIPT_MAIN: 'frontend-src/demo/scripts/main',
        SCRIPTS_OUT: 'static/demo/scripts'
    },
    barista: {
        STYLES: 'frontend-src/barista/styles/*.*',
        STYLES_OUT: 'static/barista/styles',
        FONTS: [],
        FONTS_OUT: 'static/barista/fonts',
        SCRIPT_MAIN: 'frontend-src/barista/scripts/main',
        SCRIPTS_OUT: 'static/barista/scripts'
    }
};

function registerTasks(targetName) {
    var path = targets[targetName],
        scriptsTaskName = targetName + '-scripts',
        stylesTaskName = targetName + '-styles',
        watchTaskName = targetName + '-watch';

    gulp.task(stylesTaskName, function () {
        gulp.src(path.STYLES)
            .pipe(concat('bundle.css'))
            .pipe(gulp.dest(path.STYLES_OUT));
        gulp.src(path.FONTS)
            .pipe(gulp.dest(path.FONTS_OUT));
    });

    gulp.task(scriptsTaskName, function () {
        browserify({
            entries: path.SCRIPT_MAIN,
            transform: [babelify, reactify],
            extensions: ['.jsx'],
            debug: true
        })
            .bundle()
            .on('error', function (e) {
                gutil.log('Build error: ' + e.message);
            })
            .pipe(source('bundle.js'))
            .pipe(buffer())
            .pipe(sourcemaps.init({loadMaps: true}))
            .pipe(uglify('bundle.js'))
            .pipe(sourcemaps.write('./'))
            .pipe(gulp.dest(path.SCRIPTS_OUT));
    });

    function _rebundle(x) {
        return x
            .bundle()
            .on('error', function (e) {
                gutil.log(e.message);
            })
            .pipe(source('bundle.js'))
            .pipe(gulp.dest(path.SCRIPTS_OUT)).on('finish', function () {
                gutil.log("Rebuild success");
            });
    }

    gulp.task(targetName, [scriptsTaskName, stylesTaskName]);

    gulp.task(watchTaskName, [stylesTaskName], function () {
        gulp.watch(path.STYLES, [stylesTaskName]);
        gulp.watch(path.FONTS, [stylesTaskName]);

        var watcher = watchify(browserify({
            entries: path.SCRIPT_MAIN,
            transform: [babelify, reactify],
            extensions: ['.jsx'],
            debug: true,
            cache: {}, packageCache: {}, fullPaths: true
        }));
        watcher.on('update', function () {
            gutil.log("Starting rebuild");
            _rebundle(watcher);
        });
        return _rebundle(watcher);
    });
}

var targetList = [];
for (var targetName in targets) if (targets.hasOwnProperty(targetName)) {
    registerTasks(targetName);
    targetList.push(targetName);
}

gulp.task('default', targetList);
