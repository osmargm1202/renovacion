function numberOrNull(value) {
	if (value === null || value === undefined || Number.isNaN(Number(value))) {
		return null;
	}
	return Number(value);
}

function formatNumber(value, decimals = 2) {
	const numeric = numberOrNull(value);
	if (numeric === null) return "N/A";
	return numeric.toLocaleString("en-US", {
		minimumFractionDigits: decimals,
		maximumFractionDigits: decimals,
	});
}

module.exports = { numberOrNull, formatNumber };
