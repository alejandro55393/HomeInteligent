data = readtable('C:\Users\aleja\OneDrive\Escritorio\TFG\BASEDATOS_10.03-17.03.xlsx');

% Convertir la columna FechaHora a tipo datetime
data.FechaHora = datetime(data.FechaHora, 'InputFormat', 'yyyy-MM-dd HH:mm:ss');

% Crear una variable binaria para el estado de la calefacción
data.CalefON = strcmp(data.Estado, 'ON');  % 1 si está ON, 0 si está OFF

fecha = data.FechaHora;
temp = data.Temperatura;
estadoON = data.CalefON;

% Crear figura
figure;
hold on;

% 1. Temperatura (línea azul)
lineaTemp = plot(fecha, temp, 'b', 'LineWidth', 1.3);

% 2. Umbral calefacción
umbral = 18.5;  % o el que tú uses
lineaUmbral = yline(umbral, '--k', 'Umbral calefacción', ...
    'LabelHorizontalAlignment', 'left', 'Color', [0.2 0.2 0.2]);

% 3. Sombrear zonas donde calefacción está ON
maxY = max(temp) + 1;  % Altura del área
for i = 1:length(estadoON)-1
    if estadoON(i) == 1 && estadoON(i+1) == 1
        % sombrear entre dos puntos consecutivos con calefacción ON
        area([fecha(i) fecha(i+1)], [maxY maxY], 'FaceColor', [1 0 0], ...
            'FaceAlpha', 0.15, 'EdgeAlpha', 0);
    end
end

% 4. Ejes y etiquetas
xlabel('Fecha y hora');
ylabel('Temperatura (°C)');
title('Temperatura y calefacción encendida');
grid on;

% 5. Leyenda clara
legend([lineaTemp, lineaUmbral], {'Temperatura', 'Umbral calefacción'}, 'Location', 'northwest');