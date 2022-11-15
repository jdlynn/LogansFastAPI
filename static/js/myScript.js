const startTime = document.querySelector('#startTime');
const endTime = document.querySelector('#endTime');

const setDefaults = () => {
    startTime.defaultValue = "2023-02-01T11:00";
    endTime.defaultValue = "2023-02-01T12:00";
}
 window.onload = setDefaults;