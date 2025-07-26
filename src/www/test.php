<div class="switch-container">
  <span class="switch-label">Switch</span>
  <label class="switch">
    <input type="checkbox">
    <span class="slider">
      <span class="label-on">On</span>
      <span class="label-off">Off</span>
    </span>
  </label>
</div>

<style>
  .switch-container {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: sans-serif;
  }

  .switch-label {
    font-size: 14px;
    color: #333;
  }

  .switch {
    position: relative;
    display: inline-block;
    width: 70px;
    height: 34px;
  }

  .switch input {
    opacity: 0;
    width: 0;
    height: 0;
  }

  .slider {
    position: absolute;
    cursor: pointer;
    top: 0; left: 0;
    right: 0; bottom: 0;
    background-color: #ccc;
    transition: 0.4s;
    border-radius: 34px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 8px;
    color: white;
    font-size: 12px;
  }

  .slider:before {
    content: "";
    position: absolute;
    height: 26px; width: 26px;
    left: 4px; bottom: 4px;
    background-color: white;
    transition: 0.4s;
    border-radius: 50%;
  }

  .label-on {
    visibility: hidden;
  }

  .label-off {
    visibility: visible;
  }

  input:checked + .slider {
    background-color: #2196F3;
  }

  input:checked + .slider .label-on {
    visibility: visible;
  }

  input:checked + .slider .label-off {
    visibility: hidden;
  }

  input:checked + .slider:before {
    transform: translateX(36px);
  }
</style>
