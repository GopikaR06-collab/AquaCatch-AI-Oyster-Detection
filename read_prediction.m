clc;
clear;

figure;
title("Live Oyster Detection Analytics");
xlabel("Time");
ylabel("Confidence (%)");
hold on;

conf_data = [];

while true
    if isfile('prediction.txt')
        data = fileread('prediction.txt');
        splitData = split(data, ',');

        label = splitData{1};
        confidence = str2double(splitData{2});
        size_value = splitData{3};
        distance = splitData{4};
        grade = splitData{5};

        fprintf("Detected: %s | Confidence: %.2f %% | Size: %s | Distance: %s cm | Grade: %s\n", ...
                label, confidence, size_value, distance, grade);

        conf_data = [conf_data confidence];

        plot(conf_data);
        drawnow;
    end

    pause(3);
end