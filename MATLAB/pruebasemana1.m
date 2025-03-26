% ----------------------------------------
% Paso 1: Calcular duraciones de encendido
% ----------------------------------------
data = readtable('C:\Users\aleja\OneDrive\Escritorio\TFG\BASEDATOS_10.03-17.03.xlsx');
data.CalefON = strcmp(data.Estado, 'ON');  % 1 si está ON, 0 si está OFF

% Paso 1: Umbral de corriente
umbral_corriente = 1.0;  % Ajusta si necesitas

% Paso 2: Binarizar corriente (1 si está encendida, 0 si no)
corrienteON = data.Consumo > umbral_corriente;

% Paso 3: Detectar bloques de encendido (igual que antes, pero con corriente)
encendidos = [];
contador = 0;

for i = 1:height(data)
    if corrienteON(i)
        contador = contador + 1;
    elseif contador > 0
        duracion_horas = contador * 10 / 3600;  % 10 segundos por muestra
        encendidos(end+1) = duracion_horas;
        contador = 0;
    end
end

% Por si terminó con corriente encendida
if contador > 0
    encendidos(end+1) = contador * 10 / 3600;
end

% Filtrar duración excesiva (>2 h)
encendidos_filtrados = encendidos(encendidos < 2);

% Graficar
figure;
histogram(encendidos_filtrados, 'BinWidth', 0.05, ...
    'FaceColor', [0.2 0.6 0.8], 'EdgeColor', 'black');
xlabel('Duración de encendido (horas)');
ylabel('Frecuencia');
title('Distribución real de encendidos de calefacción (por corriente)');
grid on;

% Mostrar estadísticas
fprintf('Encendidos reales detectados: %d\n', numel(encendidos));
fprintf('Media: %.2f h | Mediana: %.2f h | Máxima: %.2f h\n', ...
    mean(encendidos_filtrados), median(encendidos_filtrados), max(encendidos));