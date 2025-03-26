% Suponiendo que ya tienes cargado:
% data.FechaHora → datetime
% data.Temperatura → en °C
% data.Consumo → corriente en amperios
data = readtable('C:\Users\aleja\OneDrive\Escritorio\TFG\BASEDATOS_10.03-17.03.xlsx');

% Convertir la columna FechaHora a tipo datetime
data.FechaHora = datetime(data.FechaHora, 'InputFormat', 'yyyy-MM-dd HH:mm:ss');

% Crear una variable binaria para el estado de la calefacción
data.CalefON = strcmp(data.Estado, 'ON');  % 1 si está ON, 0 si está OFF

fecha = data.FechaHora;
temp = data.Temperatura;
estadoON = data.CalefON;
% Crear la figura
figure;

% Eje izquierdo: Temperatura
yyaxis left
plot(data.FechaHora, data.Temperatura, 'b', 'LineWidth', 1.5);
ylabel('Temperatura (°C)');
ylim([min(data.Temperatura)-1, max(data.Temperatura)+1]);

% Eje derecho: Corriente
yyaxis right
plot(data.FechaHora, data.Consumo, 'r', 'LineWidth', 1);
ylabel('Corriente (A)');
ylim([min(data.Consumo)-0.1, max(data.Consumo)+0.1]);

% Títulos y etiquetas
xlabel('Fecha y hora');
title('Temperatura y corriente eléctrica');
grid on;

% Leyenda combinada
legend('Temperatura', 'Corriente', 'Location', 'northwest');