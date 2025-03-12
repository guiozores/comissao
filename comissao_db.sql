-- phpMyAdmin SQL Dump
-- version 5.2.1deb3
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Tempo de geração: 12/03/2025 às 18:58
-- Versão do servidor: 8.0.41-0ubuntu0.24.04.1
-- Versão do PHP: 8.3.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `comissao_db`
--

-- --------------------------------------------------------

--
-- Estrutura para tabela `commissions`
--

CREATE TABLE `commissions` (
  `id` int NOT NULL,
  `month` int NOT NULL,
  `year` int NOT NULL,
  `name` varchar(200) COLLATE utf8mb4_general_ci NOT NULL,
  `original_value` float NOT NULL,
  `factor` float DEFAULT NULL,
  `reported` tinyint(1) DEFAULT NULL,
  `company_status` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `employee_status` varchar(50) COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `commissions`
--

INSERT INTO `commissions` (`id`, `month`, `year`, `name`, `original_value`, `factor`, `reported`, `company_status`, `employee_status`) VALUES
(2, 11, 2024, '7584-P-1-AF-Toyota (2 mês)', 7781, 0.5, 1, 'pago', 'pago'),
(4, 1, 2025, '7654-P-2/24 - TEC/COFCO Armazém 12-A', 6640, 0.1, 1, 'em caixa', 'pago'),
(5, 7, 2024, 'TS.P-7389-B/24 - TES (NAABSA)', 5376, 0.5, 1, 'pago', 'pago'),
(6, 11, 2024, '7322-P-2 AGEO-5-mês', 2950, 0.5, 1, 'medição aprovada', 'pago'),
(7, 1, 2025, '7486‐P-5 -TERMINAL XXXIX (T-39) (Mobilização TOPOGRAFIA)', 5250, 0.4, 1, 'pago', 'pago'),
(8, 1, 2025, '7486‐P-5 -TERMINAL XXXIX (T-39) (Marcação e nivelamento dos pontos, valor total, 39 pontos marcados x R$ 250,00)', 9750, 0.4, 1, 'em caixa', 'pago'),
(12, 1, 2024, '7336-P - NOVATA (doc)', 4760, 0.5, 1, 'pago', 'pago'),
(13, 1, 2024, '7365-P-1 - Castilho', 6460, 0.1, 1, 'pago', 'pago'),
(14, 1, 2024, '7370-P-1-T39-Coleta', 6698, 0.1, 1, 'pago', 'pago'),
(15, 2, 2024, '7371-P-2-T39-SPT', 6698, 0.1, 1, 'pago', 'pago'),
(16, 2, 2024, '7365-P-1 - Castilho', 5320, 0.5, 1, 'pago', 'pago'),
(17, 2, 2024, '7399-CPEA', 5510, 0.1, 1, 'pago', 'pago'),
(18, 3, 2024, '7373-P-2- CPEA DPW', 5400, 0.1, 1, 'pago', 'pago'),
(19, 3, 2024, '7370-P-1 T-39 COLETA', 5515, 0.5, 1, 'pago', 'pago'),
(20, 3, 2024, '7371-P-2 T-39 SPT', 6698, 0.1, 1, 'pago', 'pago'),
(21, 4, 2024, '7408-P-3-Belov', 6460, 0.1, 1, 'pago', 'pago'),
(22, 4, 2024, '7258-P-1-AmeTower', 4700, 0.5, 1, 'pago', 'pago'),
(23, 4, 2024, '7258-P-1-AmeTower', 4800, 0.1, 1, 'pago', 'pago'),
(24, 5, 2024, '7371-A-T-39-SPT (1mes)', 5515, 0.5, 1, 'pago', 'pago'),
(25, 5, 2024, '7355-A-TGG', 6698, 0.1, 1, 'pago', 'pago'),
(26, 5, 2024, '7456-P2-REV2-EO SOL', 5900, 0.1, 1, 'pago', 'pago'),
(27, 6, 2024, '7371-A-T-39-SPT (2mes)', 5515, 0.5, 1, 'pago', 'pago'),
(28, 6, 2024, '7355-A-TEG', 6528, 0.1, 1, 'pago', 'pago'),
(29, 7, 2024, '7322-P-2-AGEO', 6800, 0.1, 1, 'pago', 'pago'),
(30, 7, 2024, '7456P-2-EO Soluções', 5455, 0.5, 1, 'pago', 'pago'),
(31, 7, 2024, '7391-P-1-TEAG', 6528, 0.1, 1, 'pago', 'pago'),
(32, 7, 2024, '7385-P-1 CPEA/CESARI', 5800, 0.1, 1, 'pago', 'pago'),
(33, 8, 2024, '7425-SINER', 5460, 0.5, 1, 'pago', 'pago'),
(34, 8, 2024, '7389-P1-TES', 6528, 0.1, 1, 'pago', 'pago'),
(35, 8, 2024, '7425-SINER', 6630, 0.1, 1, 'pago', 'pago'),
(36, 8, 2024, '7373-P2-CPEA', 5400, 0.1, 1, 'pago', 'pago'),
(37, 9, 2024, '7355-P-1 TGG(NAABSA)', 5460, 0.5, 1, 'pago', 'pago'),
(38, 9, 2024, '7521-P-1 - CPEA/Ultracargo', 5800, 0.1, 1, 'pago', 'pago'),
(39, 9, 2024, '7372-P-ADM(NAABSA)', 6800, 0.1, 1, 'pago', 'pago'),
(40, 12, 2024, '7322-P-2 AGEO-6-mês', 2950, 0.5, 1, 'pago', 'pago'),
(41, 10, 2024, '7379-P-1-TEG (NAABSA)', 5367, 0.5, 1, 'pago', 'pago'),
(42, 10, 2024, '7579-P DOW', 24900, 0.5, 1, 'pago', 'pago'),
(43, 10, 2024, '7683-P-1-AF/Toyota', 7683, 0.1, 1, 'pago', 'pago'),
(44, 8, 2024, '7322-P-2 AGEO-2-mês', 2950, 0.5, 1, 'pago', 'pago'),
(45, 10, 2024, '7579-P DOW', 8200, 0.1, 1, 'pago', 'pago'),
(46, 11, 2024, '7391-P-1-TEAG (NAABSA)', 5367, 0.5, 1, 'pago', 'pago'),
(47, 9, 2024, '7322-P-2 AGEO-3-mês', 2950, 0.5, 1, 'pago', 'pago'),
(48, 12, 2024, '7584-P-1-AF-Toyota (1mes)', 7781, 0.5, 1, 'pago', 'pago'),
(49, 10, 2024, '7322-P-2 AGEO-4-mês', 2950, 0.5, 1, 'pago', 'pago'),
(50, 12, 2024, '7644-P-1-Coper(NAABSA)', 6664, 0.1, 1, 'pago', 'pago'),
(51, 1, 2025, '7322-P-2 AGEO-7-mês', 2950, 0.5, 0, 'medição aprovada', 'aguardando pagamento'),
(52, 2, 2025, '7322-P-2 AGEO-8-mês', 2950, 0.5, 0, 'medição aprovada', 'aguardando pagamento'),
(53, 7, 2024, '7322-P-2-AGEO-1-mês', 2950, 0.5, 0, 'pago', 'pago'),
(54, 4, 2024, '7408-P-3-BELOV/COFCO 1-mês', 5320, 0.5, 0, 'em caixa', 'aguardando pagamento'),
(55, 5, 2024, '7408-P-3-BELOV/COFCO 2-mês', 5320, 0.5, 0, 'em caixa', 'aguardando pagamento'),
(56, 6, 2024, '7408-P-3-BELOV/COFCO 3-mês', 5320, 0.5, 0, 'em caixa', 'aguardando pagamento'),
(57, 9, 2024, '7408-P-3-BELOV/COFCO 4-mês', 5320, 0.5, 0, 'em caixa', 'aguardando pagamento'),
(58, 8, 2024, '7372-P-ADM(NAABSA)', 5600, 0.5, 0, 'em caixa', 'aguardando pagamento'),
(59, 2, 2025, '7688-P-T-Grão(NAABSA)', 7800, 0.1, 0, 'medição aprovada', 'aguardando pagamento'),
(60, 2, 2025, '7688-P-T-Grão(NAABSA)', 8150, 0.5, 0, 'medição aprovada', 'aguardando pagamento'),
(61, 1, 2025, '7688-P-1-FACTTUM(T-39)', 6200, 0.5, 0, 'medição aprovada', 'aguardando pagamento'),
(62, 1, 2025, '7654-P-2/24 - TEC/COFCO Armazém 12-A', 5488, 0.5, 0, 'em caixa', 'aguardando pagamento'),
(63, 10, 2024, '7486‐P-5 -TERMINAL XXXIX (T-39)-1-mês', 4980, 0.5, 0, 'em caixa', 'aguardando pagamento'),
(64, 11, 2024, '7486‐P-5 -TERMINAL XXXIX (T-39)-2-mês', 4980, 0.5, 0, 'em caixa', 'aguardando pagamento'),
(65, 12, 2024, '7486‐P-5 -TERMINAL XXXIX (T-39)-3-mês', 4980, 0.5, 0, 'medição aprovada', 'aguardando pagamento'),
(66, 1, 2025, '7486‐P-5 -TERMINAL XXXIX (T-39)-4-mês', 4980, 0.5, 0, 'medição aprovada', 'aguardando pagamento'),
(67, 2, 2025, '7486‐P-5 -TERMINAL XXXIX (T-39)-5-mês', 4980, 0.5, 0, 'medição aprovada', 'aguardando pagamento'),
(68, 12, 2024, '7644-P-1-Coper(NAABSA)', 5488, 0.5, 0, 'em caixa', 'aguardando pagamento');

-- --------------------------------------------------------

--
-- Estrutura para tabela `expenses`
--

CREATE TABLE `expenses` (
  `id` int NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `value` float NOT NULL,
  `month` int NOT NULL,
  `year` int NOT NULL,
  `is_recurring` tinyint(1) DEFAULT NULL,
  `installment_info` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `expenses`
--

INSERT INTO `expenses` (`id`, `name`, `value`, `month`, `year`, `is_recurring`, `installment_info`) VALUES
(7, 'Seguro veículo', 87.5, 2, 2025, 1, '8/12'),
(9, 'ChatGPT Plus', 100, 2, 2025, 1, ''),
(10, 'Almoço - Classificação Sábado', 40, 1, 2025, 0, ''),
(11, 'Ring Light - Luz p/ Classificação', 239, 1, 2025, 0, ''),
(12, 'LITORAL PLAZA PARK SHOPPING - Passagem referente à placa STC-2G43 (Realização de ASO, Perfil)', 8, 1, 2025, 0, '');

-- --------------------------------------------------------

--
-- Estrutura para tabela `fixed_costs`
--

CREATE TABLE `fixed_costs` (
  `id` int NOT NULL,
  `vivo` float NOT NULL,
  `va` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `fixed_costs`
--

INSERT INTO `fixed_costs` (`id`, `vivo`, `va`) VALUES
(1, 120, 600);

-- --------------------------------------------------------

--
-- Estrutura para tabela `monthly_reports`
--

CREATE TABLE `monthly_reports` (
  `id` int NOT NULL,
  `report_month` int NOT NULL,
  `report_year` int NOT NULL,
  `generated_date` datetime NOT NULL,
  `total_commissions` float NOT NULL,
  `total_expenses` float NOT NULL,
  `grand_total` float NOT NULL,
  `commissions_data` text COLLATE utf8mb4_general_ci,
  `expenses_data` text COLLATE utf8mb4_general_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Despejando dados para a tabela `monthly_reports`
--

INSERT INTO `monthly_reports` (`id`, `report_month`, `report_year`, `generated_date`, `total_commissions`, `total_expenses`, `grand_total`, `commissions_data`, `expenses_data`) VALUES
(12, 1, 2025, '2025-02-05 23:46:33', 100, 530, 630, '[{\"id\": 1, \"name\": \"treste 21312312ddsa\", \"month\": 1, \"year\": 2025, \"original_value\": 1000.0, \"factor\": 0.1, \"status\": \"aguardando\", \"computed_value\": 100.0}]', '[{\"id\": 2, \"name\": \"teste\", \"value\": 50.0, \"month\": 1, \"year\": 2025, \"installment_info\": \"\", \"is_recurring\": false}, {\"id\": 3, \"name\": \"pedagio imigrantes\", \"value\": 50.0, \"month\": 1, \"year\": 2025, \"installment_info\": \"\", \"is_recurring\": false}, {\"id\": 4, \"name\": \"teste2 9\", \"value\": 90.0, \"month\": 1, \"year\": 2025, \"installment_info\": \"\", \"is_recurring\": false}, {\"id\": 5, \"name\": \"viralata\", \"value\": 90.0, \"month\": 1, \"year\": 2025, \"installment_info\": \"\", \"is_recurring\": false}, {\"id\": 6, \"name\": \"penes de boi\", \"value\": 50.0, \"month\": 1, \"year\": 2025, \"installment_info\": \"\", \"is_recurring\": false}, {\"id\": 1, \"name\": \"teste\", \"value\": 200.0, \"month\": 1, \"year\": 2025, \"installment_info\": \"2/12\", \"is_recurring\": true}]'),
(19, 2, 2025, '2025-03-06 23:17:42', 10163, 907.5, 11070.5, '[{\"id\": 5, \"name\": \"TS.P-7389-B/24 - TES (NAABSA)\", \"month\": 7, \"year\": 2024, \"original_value\": 5376.0, \"factor\": 0.5, \"status\": \"aguardando\", \"computed_value\": 2688.0}, {\"id\": 6, \"name\": \"7322-P-2 AGEO-(6 m\\u00eas) de 8\", \"month\": 11, \"year\": 2024, \"original_value\": 2950.0, \"factor\": 0.5, \"status\": \"aguardando\", \"computed_value\": 1475.0}, {\"id\": 7, \"name\": \"TS.P\\u20107486\\u2010C/24 - TERMINAL XXXIX (Mobiliza\\u00e7\\u00e3o TOPOGRAFIA)\", \"month\": 1, \"year\": 2025, \"original_value\": 5250.0, \"factor\": 0.4, \"status\": \"aguardando\", \"computed_value\": 2100.0}, {\"id\": 8, \"name\": \"TS.P\\u20107486\\u2010C/24 - TERMINAL XXXIX (Marca\\u00e7\\u00e3o e nivelamento dos pontos, valor total, 39 pontos marcados x R$ 250,00)\", \"month\": 1, \"year\": 2025, \"original_value\": 9750.0, \"factor\": 0.4, \"status\": \"aguardando\", \"computed_value\": 3900.0}]', '[{\"id\": 7, \"name\": \"Seguro ve\\u00edculo\", \"value\": 87.5, \"month\": 2, \"year\": 2025, \"installment_info\": \"1/12\", \"is_recurring\": true}, {\"id\": 9, \"name\": \"ChatGPT Plus\", \"value\": 100.0, \"month\": 2, \"year\": 2025, \"installment_info\": \"\", \"is_recurring\": true}]'),
(21, 4, 2025, '2025-03-11 13:24:53', 0, 907.5, 907.5, '[]', '[{\"id\": 7, \"name\": \"Seguro ve\\u00edculo\", \"value\": 87.5, \"month\": 2, \"year\": 2025, \"installment_info\": \"8/12\", \"is_recurring\": true}, {\"id\": 9, \"name\": \"ChatGPT Plus\", \"value\": 100.0, \"month\": 2, \"year\": 2025, \"installment_info\": \"\", \"is_recurring\": true}]'),
(25, 1, 2025, '2025-03-11 19:48:58', 6029.5, 1194.5, 7224, '[{\"id\": 2, \"name\": \"7584-P-1-AF-Toyota (2 m\\u00eas)\", \"month\": 11, \"year\": 2024, \"original_value\": 7781.0, \"factor\": 0.5, \"company_status\": \"em caixa\", \"employee_status\": \"aguardando pagamento\", \"computed_value\": 3890.5}, {\"id\": 3, \"name\": \"7322-P-2 AGEO-(5 m\\u00eas) de 8\", \"month\": 12, \"year\": 2024, \"original_value\": 2950.0, \"factor\": 0.5, \"company_status\": \"medi\\u00e7\\u00e3o aprovada\", \"employee_status\": \"pago\", \"computed_value\": 1475.0}, {\"id\": 4, \"name\": \"7654-P-2/24 - TEC/COFCO Armaz\\u00e9m 12-A\", \"month\": 1, \"year\": 2025, \"original_value\": 6640.0, \"factor\": 0.1, \"company_status\": \"em caixa\", \"employee_status\": \"aguardando pagamento\", \"computed_value\": 664.0}]', '[{\"id\": 10, \"name\": \"Almo\\u00e7o - Classifica\\u00e7\\u00e3o S\\u00e1bado\", \"value\": 40.0, \"month\": 1, \"year\": 2025, \"installment_info\": \"\", \"is_recurring\": false}, {\"id\": 11, \"name\": \"Ring Light - Luz p/ Classifica\\u00e7\\u00e3o\", \"value\": 239.0, \"month\": 1, \"year\": 2025, \"installment_info\": \"\", \"is_recurring\": false}, {\"id\": 12, \"name\": \"LITORAL PLAZA PARK SHOPPING - Passagem referente \\u00e0 placa STC-2G43 (Realiza\\u00e7\\u00e3o de ASO, Perfil)\", \"value\": 8.0, \"month\": 1, \"year\": 2025, \"installment_info\": \"\", \"is_recurring\": false}, {\"id\": 7, \"name\": \"Seguro ve\\u00edculo\", \"value\": 87.5, \"month\": 2, \"year\": 2025, \"installment_info\": \"8/12\", \"is_recurring\": true}, {\"id\": 9, \"name\": \"ChatGPT Plus\", \"value\": 100.0, \"month\": 2, \"year\": 2025, \"installment_info\": \"\", \"is_recurring\": true}]');

--
-- Índices para tabelas despejadas
--

--
-- Índices de tabela `commissions`
--
ALTER TABLE `commissions`
  ADD PRIMARY KEY (`id`);

--
-- Índices de tabela `expenses`
--
ALTER TABLE `expenses`
  ADD PRIMARY KEY (`id`);

--
-- Índices de tabela `fixed_costs`
--
ALTER TABLE `fixed_costs`
  ADD PRIMARY KEY (`id`);

--
-- Índices de tabela `monthly_reports`
--
ALTER TABLE `monthly_reports`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT para tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `commissions`
--
ALTER TABLE `commissions`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=70;

--
-- AUTO_INCREMENT de tabela `expenses`
--
ALTER TABLE `expenses`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de tabela `fixed_costs`
--
ALTER TABLE `fixed_costs`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de tabela `monthly_reports`
--
ALTER TABLE `monthly_reports`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
