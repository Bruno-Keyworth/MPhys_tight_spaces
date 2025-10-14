% Folder containing your images
folder = '/data/test_photos';

% Get list of all .tiff files
files = dir(fullfile(folder, '*.tiff'));

% Preallocate arrays
n = length(files);
index_vals = zeros(n, 1);
decimal_vals = zeros(n, 1);

for k = 1:n
    filename = files(k).name;

    % Split filename by underscore
    parts = split(filename, '_');
    index_str = parts{1};
    hex_str = erase(parts{2}, '.tiff');  % remove extension

    % Convert strings to numbers
    index_vals(k) = str2double(index_str);
    decimal_vals(k) = hex2dec(hex_str);

    % Optionally read the image
    % img = imread(fullfile(folder, filename));

    fprintf('File %d: index = %d, hex = %s, decimal = %d\n', ...
        k, index_vals(k), hex_str, decimal_vals(k));
end