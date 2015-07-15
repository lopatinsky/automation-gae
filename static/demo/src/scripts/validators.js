export function required(message) {
    return function validateRequired(value) {
        if (!value) {
            return message;
        }
        return false;
    }
}

export function pattern(regex, message) {
    return function validatePattern(value) {
        if (!value.match(regex)) {
            return message;
        }
        return false;
    }
}

export function email(message) {
    return pattern(/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,6}$/i, message);
}
